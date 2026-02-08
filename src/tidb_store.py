
import os
import mysql.connector
from mysql.connector import Error
import json
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from config import TIDB_HOST, TIDB_PORT, TIDB_USER, TIDB_PASSWORD, TIDB_DATABASE, TIDB_CA_PATH

class TiDBGraph:
    def __init__(self):
        self.config = {
            'host': TIDB_HOST,
            'port': TIDB_PORT,
            'user': TIDB_USER,
            'password': TIDB_PASSWORD,
            'database': TIDB_DATABASE
        }
        if TIDB_CA_PATH:
            self.config['ssl_ca'] = TIDB_CA_PATH
            self.config['ssl_verify_cert'] = True

        self._init_schema()

    def get_connection(self):
        try:
            connection = mysql.connector.connect(**self.config)
            return connection
        except Error as e:
            logger.error(f"Error connecting to TiDB: {e}")
            raise e

    def _init_schema(self):
        """Initializes the database schema for Graph and Vector storage."""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            
            # Nodes Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS nodes (
                    id VARCHAR(255) PRIMARY KEY,
                    type VARCHAR(100),
                    properties JSON,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

            # Edges Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS edges (
                    source VARCHAR(255),
                    target VARCHAR(255),
                    type VARCHAR(100),
                    properties JSON,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (source, target, type),
                    FOREIGN KEY (source) REFERENCES nodes(id) ON DELETE CASCADE,
                    FOREIGN KEY (target) REFERENCES nodes(id) ON DELETE CASCADE
                );
            """)

            # Chunks Table for Vector Search
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS chunks (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    content TEXT,
                    source VARCHAR(255),
                    page INT,
                    embedding VECTOR(384),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

            conn.commit()
            logger.info("Schema initialized (nodes, edges, chunks tables).")
        except Error as e:
            logger.error(f"Error initializing schema: {e}")
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()

    def query(self, sql, params=None):
        """Executes a generic SQL query."""
        conn = self.get_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(sql, params or ())
            if sql.strip().upper().startswith("SELECT"):
                result = cursor.fetchall()
                return result
            else:
                conn.commit()
                return cursor.rowcount
        except Error as e:
            logger.error(f"Error executing query: {e}\nSQL: {sql}\nParams: {params}")
            raise e
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()
    
    # --- Graph Methods ---

    def merge_node(self, node_id, node_type, properties=None):
        """Upserts a node."""
        properties_json = json.dumps(properties or {})
        sql = """
            INSERT INTO nodes (id, type, properties) 
            VALUES (%s, %s, %s) 
            ON DUPLICATE KEY UPDATE 
            type=VALUES(type), properties=VALUES(properties);
        """
        self.query(sql, (node_id, node_type, properties_json))

    def merge_edge(self, source, target, rel_type, properties=None):
        """Upserts an edge."""
        properties_json = json.dumps(properties or {})
        sql = """
            INSERT INTO edges (source, target, type, properties) 
            VALUES (%s, %s, %s, %s) 
            ON DUPLICATE KEY UPDATE 
            properties=VALUES(properties);
        """
        try:
            self.query(sql, (source, target, rel_type, properties_json))
        except Error as e:
             # Handle case where nodes don't exist yet (though we should usually create nodes first)
             logger.error(f"Failed to create edge {source} -> {target}: {e}")

    def batch_insert_graph_data(self, nodes, edges):
        """
        Inserts multiple nodes and edges in a single transaction/connection.
        nodes: list of dicts {'id': str, 'type': str, 'properties': dict}
        edges: list of dicts {'source': str, 'target': str, 'type': str, 'properties': dict}
        """
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            
            # 1. Insert Nodes
            node_sql = """
                INSERT INTO nodes (id, type, properties) 
                VALUES (%s, %s, %s) 
                ON DUPLICATE KEY UPDATE 
                type=VALUES(type), properties=VALUES(properties);
            """
            node_data = []
            for n in nodes:
                node_data.append((
                    n['id'], 
                    n['type'], 
                    json.dumps(n.get('properties', {}))
                ))
            
            if node_data:
                cursor.executemany(node_sql, node_data)
            
            # 2. Insert Edges
            edge_sql = """
                INSERT INTO edges (source, target, type, properties) 
                VALUES (%s, %s, %s, %s) 
                ON DUPLICATE KEY UPDATE 
                properties=VALUES(properties);
            """
            edge_data = []
            for e in edges:
                edge_data.append((
                    e['source'], 
                    e['target'], 
                    e['type'], 
                    json.dumps(e.get('properties', {}))
                ))
            
            if edge_data:
                cursor.executemany(edge_sql, edge_data)
            
            conn.commit()
            logger.info(f"Batch inserted {len(nodes)} nodes and {len(edges)} edges.")
            
        except Error as e:
            logger.error(f"Error in batch insert: {e}")
            # Don't raise, just log, to allow processing to continue (or raise if strict)
            raise e
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()

    def get_schema(self):
        """Returns a string representation of the schema for LLM context."""
        return """
        Table 'nodes': id (VARCHAR PK), type (VARCHAR), properties (JSON)
        Table 'edges': source (VARCHAR FK), target (VARCHAR FK), type (VARCHAR), properties (JSON)
        Table 'chunks': id (INT PK), content (TEXT), source (VARCHAR), page (INT), embedding (VECTOR<384>)
        """

    # --- Vector Methods ---

    def insert_chunk(self, content, source, page, embedding):
        """Inserts a text chunk with its vector embedding."""
        # Note: mysql-connector-python might handle list->vector conversion if formatted as string or list
        # TiDB Vector expects a string representation like '[0.1, 0.2, ...]'
        embedding_str = str(embedding)
        sql = """
            INSERT INTO chunks (content, source, page, embedding)
            VALUES (%s, %s, %s, VEC_FROM_TEXT(%s));
        """
        self.query(sql, (content, source, page, embedding_str))

    def search_vectors(self, query_embedding, top_k=5, file_filters=None):
        """Searches for similar chunks using Cosine Distance, optionally filtering by source file."""
        embedding_str = str(query_embedding)
        
        where_clause = ""
        params = [embedding_str]
        
        if file_filters:
            # Create placeholders for the IN clause
            # We use LIKE matches because the source column might be a full path while filter is just filename
            # OR we can assume file_filters are substrings.
            # Let's use a logic where we check if source ends with any of the filters
            # This is robust because source usually stores relative or absolute path ending with filename.
             
            # Constructing a dynamic OR clause: (source LIKE %f1 OR source LIKE %f2 ...)
            conditions = []
            img_params = []
            for f in file_filters:
                conditions.append("source LIKE %s")
                # Add wildcard before filename to match full path ending with filename
                img_params.append(f"%{f}")
            
            if conditions:
                where_clause = "WHERE (" + " OR ".join(conditions) + ")"
                params.extend(img_params)
        
        params.append(top_k)

        sql = f"""
            SELECT content, source, page, 
                   VEC_COSINE_DISTANCE(embedding, VEC_FROM_TEXT(%s)) AS distance
            FROM chunks
            {where_clause}
            ORDER BY distance ASC
            LIMIT %s;
        """
        return self.query(sql, tuple(params))

    def clear_data(self):
        """Clears all data from tables (for testing)."""
        # Order matters due to foreign keys
        self.query("DROP TABLE IF EXISTS edges;")
        self.query("DROP TABLE IF EXISTS nodes;")
        self.query("DROP TABLE IF EXISTS chunks;")
        logger.info("All tables dropped. They will be recreated on next run.")
