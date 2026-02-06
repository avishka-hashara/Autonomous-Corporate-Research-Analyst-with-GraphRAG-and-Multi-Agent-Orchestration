from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os

def create_dummy_pdf():
    if not os.path.exists("data"):
        os.makedirs("data")
    
    c = canvas.Canvas("data/strategy_report.pdf", pagesize=letter)
    
    text = """
    CONFIDENTIAL: PROJECT TITAN STRATEGY 2026
    
    1. Executive Summary
    TechCorp Inc. is initiating "Project Titan" to acquire NovaSystems. 
    The acquisition is led by Sarah Connor, VP of Engineering. 
    However, regulatory risks remain high due to the monopoly investigation by the FTC.
    
    2. Key Stakeholders
    - Sarah Connor (VP Engineering) reports to John Smith (CEO).
    - Michael Ross (CFO) has approved the budget of $500M.
    - NovaSystems is currently sued by CyberDyne regarding patent infringement.
    
    3. Timeline
    Phase 1 starts in Q1 2026.
    Phase 2 depends on the approval from the European Commission.
    """
    
    text_lines = text.split('\n')
    y = 750
    for line in text_lines:
        c.drawString(100, y, line.strip())
        y -= 20
        
    c.save()
    print("Created data/strategy_report.pdf")

if __name__ == "__main__":
    create_dummy_pdf()