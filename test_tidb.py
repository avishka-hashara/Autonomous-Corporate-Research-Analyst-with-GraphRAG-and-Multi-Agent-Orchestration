import os
import sys
import unittest
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from tidb_store import TiDBGraph

class TestTiDBGraph(unittest.TestCase):
    def setUp(self):
        self.graph = TiDBGraph()
        # Clean up before test
        self.graph.query("DELETE FROM edges")
        self.graph.query("DELETE FROM nodes")
        self.graph.query("DELETE FROM chunks")

    def test_connection(self):
        conn = self.graph.get_connection()
        self.assertTrue(conn.is_connected())
        conn.close()

    def test_merge_node(self):
        self.graph.merge_node("node1", "TestNode", {"prop": "val"})
        result = self.graph.query("SELECT * FROM nodes WHERE id='node1'")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['type'], "TestNode")
        
    def test_merge_edge(self):
        self.graph.merge_node("node1", "TestNode")
        self.graph.merge_node("node2", "TestNode")
        self.graph.merge_edge("node1", "node2", "RELATED_TO", {"weight": 1})
        
        result = self.graph.query("SELECT * FROM edges WHERE source='node1' AND target='node2'")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['type'], "RELATED_TO")

    def test_vector_insert_search(self):
        self.graph.insert_chunk("test content", "test.pdf", 1, [0.1]*768)
        
        # Test Search
        results = self.graph.search_vectors([0.1]*768, top_k=1)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['content'], "test content")

if __name__ == '__main__':
    unittest.main()
