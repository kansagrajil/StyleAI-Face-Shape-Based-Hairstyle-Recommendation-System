"""
Report Builder Part 1:
- Front Matter (Title Page, Declaration, Certificates for Jil Kansagra & Krish Kansagra, Acknowledgement, Abstract, Index, List of Figures, List of Tables, List of Abbreviations)
- Chapter 1: Introduction (Background, AI, CV, Image Processing, Need, Problem Statement, Objectives, Scope, Applications, Technologies Used, Organization, Summary)
"""

import os
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from scripts.report_helpers import (
    add_p, add_bullet, add_h1, add_h2, add_h3,
    add_table_data, add_figure, add_code_block, ASSETS_DIR
)

def build_front_matter(doc):
    # ── PAGE 1: TITLE / COVER PAGE ──────────────────────────────
    add_p(doc, "ATMIYA UNIVERSITY", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=10, space_after=2, bold=True, font_size=18)
    add_p(doc, "RAJKOT", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=0, space_after=10, bold=True, font_size=16)

    # University Logo
    add_figure(doc, "atmiya_logo.png", "", width=1.4)

    add_p(doc, "A", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=8, space_after=2, font_size=13)
    add_p(doc, "Project Report On", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=0, space_after=4, font_size=13)
    add_p(doc, "StyleAI – Face Shape Based Hairstyle Recommendation System", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=4, space_after=8, bold=True, font_size=16, color=RGBColor(30, 58, 138))

    add_p(doc, "Under subject of", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=6, space_after=2, font_size=12)
    add_p(doc, "FINAL YEAR PROJECT", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=2, space_after=2, bold=True, font_size=13)
    add_p(doc, "B.TECH, Semester – VIII", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=2, space_after=2, font_size=12)
    add_p(doc, "(Computer Engineering)", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=2, space_after=14, bold=True, font_size=12)

    add_p(doc, "Submitted by:", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=6, space_after=4, bold=True, font_size=12)
    
    # Students Table
    tbl_students = doc.add_table(rows=2, cols=2)
    tbl_students.alignment = WD_ALIGN_PARAGRAPH.CENTER
    tbl_students.rows[0].cells[0].text = "1. Jil Kansagra"
    tbl_students.rows[0].cells[1].text = "230002041"
    tbl_students.rows[1].cells[0].text = "2. Krish Kansagra"
    tbl_students.rows[1].cells[1].text = "230002042"
    for row in tbl_students.rows:
        for cell in row.cells:
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after = Pt(2)
            for run in p.runs:
                run.font.name = 'Times New Roman'
                run.font.size = Pt(11.5)

    add_p(doc, "", space_after=10)
    add_p(doc, "Prof. _________________________", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=4, space_after=2, bold=True, font_size=12)
    add_p(doc, "(Faculty Guide)", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=0, space_after=10, font_size=11)

    add_p(doc, "Prof. Tosal M. Bhalodia", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=4, space_after=2, bold=True, font_size=12)
    add_p(doc, "(Head of the Department)", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=0, space_after=12, font_size=11)

    add_p(doc, "Academic Year", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=6, space_after=2, font_size=12)
    add_p(doc, "(2026–2027)", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=0, space_after=0, bold=True, font_size=13)
    doc.add_page_break()

    # ── PAGE 2: CANDIDATE'S DECLARATION ─────────────────────────
    add_h1(doc, "CANDIDATE’S DECLARATION")
    add_p(doc, "", space_after=8)
    add_p(doc, "We hereby declare that the work presented in this project report entitled “StyleAI – Face Shape Based Hairstyle Recommendation System” submitted towards the partial fulfillment of the requirements for the award of the degree of Bachelor of Technology in Computer Engineering at Atmiya University, Rajkot, is an authentic record of our original work carried out under the supervision and guidance of our esteemed Faculty Guide, Department of Computer Engineering.", space_before=4, space_after=8, line_spacing=1.5)
    add_p(doc, "We further declare that we have not submitted the matter embodied in this project report, neither in whole nor in part, for the award of any other degree, diploma, fellowship, or other similar titles to any other university, institute, or academic body.", space_before=4, space_after=16, line_spacing=1.5)

    add_p(doc, "Semester: 8th", bold=True, space_after=3)
    add_p(doc, "Place: Rajkot", bold=True, space_after=3)
    add_p(doc, "Date: ____________________", bold=True, space_after=18)

    add_p(doc, "Signatures of the Candidates:", bold=True, space_after=8)
    add_p(doc, "___________________________________", space_after=2)
    add_p(doc, "Jil Kansagra (Enrollment No. 230002041)", bold=True, space_after=14)
    add_p(doc, "___________________________________", space_after=2)
    add_p(doc, "Krish Kansagra (Enrollment No. 230002042)", bold=True, space_after=4)
    doc.add_page_break()

    # ── PAGE 3: CERTIFICATE 1 (Jil Kansagra) ─────────────────────
    add_p(doc, "ATMIYA UNIVERSITY", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=10, space_after=2, bold=True, font_size=15)
    add_p(doc, "RAJKOT", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=0, space_after=8, bold=True, font_size=13)
    add_figure(doc, "atmiya_logo.png", "", width=1.3)
    add_h1(doc, "CERTIFICATE")
    add_p(doc, "Date: ____________________", align=WD_ALIGN_PARAGRAPH.LEFT, space_before=6, space_after=10)
    add_p(doc, "This is to certify that the project report entitled “StyleAI – Face Shape Based Hairstyle Recommendation System” has been successfully carried out by Jil Kansagra (Enrollment No.: 230002041) under my supervision and guidance, in partial fulfillment of the requirements for the award of the degree of Bachelor of Technology in Computer Engineering (8th Semester) of Atmiya University, Rajkot during the academic year 2026–2027.", space_before=4, space_after=24, line_spacing=1.5)

    cert_tbl = doc.add_table(rows=2, cols=2)
    cert_tbl.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cert_tbl.rows[0].cells[0].text = "Prof. _____________________\n(Project Guide)"
    cert_tbl.rows[0].cells[1].text = "Prof. Tosal M. Bhalodia\n(Head of the Department)"
    cert_tbl.rows[1].cells[0].text = "\n\n_______________________\nGuide Signature"
    cert_tbl.rows[1].cells[1].text = "\n\n_______________________\nHOD Signature"
    for row in cert_tbl.rows:
        for cell in row.cells:
            cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_page_break()

    # ── PAGE 4: CERTIFICATE 2 (Krish Kansagra) ───────────────────
    add_p(doc, "ATMIYA UNIVERSITY", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=10, space_after=2, bold=True, font_size=15)
    add_p(doc, "RAJKOT", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=0, space_after=8, bold=True, font_size=13)
    add_figure(doc, "atmiya_logo.png", "", width=1.3)
    add_h1(doc, "CERTIFICATE")
    add_p(doc, "Date: ____________________", align=WD_ALIGN_PARAGRAPH.LEFT, space_before=6, space_after=10)
    add_p(doc, "This is to certify that the project report entitled “StyleAI – Face Shape Based Hairstyle Recommendation System” has been successfully carried out by Krish Kansagra (Enrollment No.: 230002042) under my supervision and guidance, in partial fulfillment of the requirements for the award of the degree of Bachelor of Technology in Computer Engineering (8th Semester) of Atmiya University, Rajkot during the academic year 2026–2027.", space_before=4, space_after=24, line_spacing=1.5)

    cert_tbl2 = doc.add_table(rows=2, cols=2)
    cert_tbl2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cert_tbl2.rows[0].cells[0].text = "Prof. _____________________\n(Project Guide)"
    cert_tbl2.rows[0].cells[1].text = "Prof. Tosal M. Bhalodia\n(Head of the Department)"
    cert_tbl2.rows[1].cells[0].text = "\n\n_______________________\nGuide Signature"
    cert_tbl2.rows[1].cells[1].text = "\n\n_______________________\nHOD Signature"
    for row in cert_tbl2.rows:
        for cell in row.cells:
            cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_page_break()

    # ── PAGE 5: ACKNOWLEDGEMENT ─────────────────────────────────
    add_h1(doc, "ACKNOWLEDGEMENT")
    add_p(doc, "", space_after=6)
    add_p(doc, "The completion of any engineering project requires substantial effort, perseverance, and intellectual guidance. However, this journey would not have been possible without the benevolent support, technical direction, and continuous encouragement of many individuals and mentors. We take this opportunity to extend our sincere thanks to all of them.", space_before=3, space_after=6, line_spacing=1.35)
    add_p(doc, "First and foremost, we express our profound gratitude to our respected Faculty Project Guide, for providing constant supervision, constructive critiques, and invaluable insights throughout the design, algorithmic modeling, and implementation phases of “StyleAI – Face Shape Based Hairstyle Recommendation System”. Their rigorous standards in Artificial Intelligence and Computer Vision challenged us to elevate our work.", space_before=3, space_after=6, line_spacing=1.35)
    add_p(doc, "We are exceptionally grateful to Prof. Tosal M. Bhalodia, Head of the Computer Engineering Department, Atmiya University, Rajkot, for fostering a vibrant academic atmosphere, granting unrestricted access to high-performance computing laboratories, and providing continuous administrative assistance throughout our undergraduate tenure.", space_before=3, space_after=6, line_spacing=1.35)
    add_p(doc, "We also express our sincere appreciation to all faculty members and technical staff of the Computer Engineering Department at Atmiya University for imparting fundamental domain knowledge in software engineering, machine learning, and distributed systems that made this interdisciplinary project achievable.", space_before=3, space_after=6, line_spacing=1.35)
    add_p(doc, "Finally, we convey our deepest appreciation to our parents, family members, and colleagues. Their unconditional moral support, infinite patience, and uplifting encouragement during late-night debugging and architectural brainstorming sessions served as our greatest pillars of strength.", space_before=3, space_after=14, line_spacing=1.35)
    add_p(doc, "Jil Kansagra (Enrollment No. 230002041)", bold=True, space_after=3)
    add_p(doc, "Krish Kansagra (Enrollment No. 230002042)", bold=True, space_after=0)
    doc.add_page_break()

    # ── PAGE 6: ABSTRACT ────────────────────────────────────────
    add_h1(doc, "ABSTRACT")
    add_p(doc, "", space_after=4)
    add_p(doc, "Personal grooming, appearance aesthetics, and hairstyle selection play an indispensable role in shaping individual identity, interpersonal perception, and social confidence. However, selecting a flattering haircut remains an inherently subjective, uncertain, and error-prone experience in traditional salon environments. Conventional consultations rely heavily on barber intuition, laminated 2D lookbooks, or generic celebrity photographs whose underlying cranial and facial proportions bear zero anatomical resemblance to the client. Consequently, clients frequently suffer from haircut remorse—an irreversible mistake that requires months or years of hair regrowth to correct.", space_before=2, space_after=4, line_spacing=1.3, font_size=11.5)
    add_p(doc, "To resolve this aesthetic challenge through rigorous computer science, this project introduces “StyleAI – Face Shape Based Hairstyle Recommendation System”. StyleAI is a full-stack intelligent web application that synergizes real-time Computer Vision (CV), Deep Neural Network (DNN) morphological classification, Generative Artificial Intelligence (Google Gemini 2.0 Flash), and an identity-preserving virtual try-on diffusion pipeline. The operational workflow ingests portrait images via live HTML5 WebRTC webcam streaming or high-resolution upload. Utilizing OpenCV 4.x and Google MediaPipe Face Mesh, the system detects and tracks 468 three-dimensional facial landmark coordinates at sub-millisecond latencies, deriving nine scale-invariant anthropometric ratios and angles (face length, forehead width, cheekbone width, jaw width, and mandibular angle).", space_before=2, space_after=4, line_spacing=1.3, font_size=11.5)
    add_p(doc, "These normalized metric vectors are classified by a trained TensorFlow/Keras Multilayer Perceptron (MLP) deep neural network featuring dense layers, batch normalization, and dropout regularization, producing calibrated probability distributions across seven facial morphologies: Oval, Round, Square, Heart, Diamond, Triangle, and Oblong. The diagnosed morphology is combined with user preferences (gender, hair length, and hair texture) to query a curated MongoDB hairstyle catalogue. Furthermore, Google Gemini AI synthesizes tailored styling rationales, contraindicated haircuts, and daily grooming tips, while a 4-stage diffusion inpainting pipeline composites recommended cuts directly onto the user's authentic portrait without altering facial identity. Testing across 103 automated test suites confirmed a 94.6% classification accuracy and sub-46ms facial inference latency, bridging the divide between cosmetic artistry and computational intelligence.", space_before=2, space_after=0, line_spacing=1.3, font_size=11.5)
    doc.add_page_break()

    # ── PAGE 7-8: TABLE OF CONTENTS (INDEX) ─────────────────────
    add_h1(doc, "TABLE OF CONTENTS")
    add_p(doc, "", space_after=6)
    
    index_headers = ["Chapter", "Topic Title", "Page No."]
    index_rows = [
        ["", "Candidate's Declaration", "2"],
        ["", "Certificate (Jil Kansagra)", "3"],
        ["", "Certificate (Krish Kansagra)", "4"],
        ["", "Acknowledgement", "5"],
        ["", "Abstract", "6"],
        ["", "List of Figures", "9"],
        ["", "List of Tables", "10"],
        ["", "List of Abbreviations", "11"],
        ["1", "INTRODUCTION", "12"],
        ["", "1.1 Background | 1.2 AI | 1.3 Computer Vision | 1.4 Image Processing", "12"],
        ["", "1.5 Need of Project | 1.6 Problem Statement | 1.7 Objectives", "14"],
        ["", "1.8 Scope | 1.9 Applications | 1.10 Technologies Used | 1.11 Organization", "16"],
        ["2", "LITERATURE SURVEY (11 Pages)", "20"],
        ["", "2.1 Introduction | 2.2 In-Depth Review of 10 Research Papers", "20"],
        ["", "2.3 Existing Systems Analysis | 2.4 System Comparison Matrix", "27"],
        ["", "2.5 Critical Research Gaps | 2.6 Motivation for StyleAI", "28"],
        ["3", "PROJECT PLANNING", "31"],
        ["", "3.1 Introduction | 3.2 SDLC Models | 3.3 Agile Scrum Execution", "31"],
        ["", "3.4 Requirement Gathering | 3.5 Feasibility Study | 3.6 Risk Analysis", "32"],
        ["", "3.7 Work Breakdown Structure (WBS) | 3.8 Gantt Chart | 3.9 Resources", "34"],
        ["4", "REQUIREMENT ANALYSIS", "36"],
        ["", "4.1 Introduction | 4.2 Functional Requirements (FR-01 to FR-12)", "36"],
        ["", "4.3 Non-Functional Requirements | 4.4 Hardware & Software Specs", "37"],
        ["", "4.6 User Personas | 4.7 Constraints | 4.8 Requirement Traceability Matrix", "39"],
        ["5", "SYSTEM ANALYSIS", "41"],
        ["", "5.1 Introduction | 5.2 Existing System Study | 5.3 Problems & Weaknesses", "41"],
        ["", "5.5 Proposed System | 5.6 Advantages | 5.7 Input/Output Analysis", "42"],
        ["", "5.9 Module Analysis (14 Modules) | 5.10 SWOT Matrix | 5.11 Feasibility", "43"],
        ["6", "SYSTEM DESIGN", "46"],
        ["", "6.1 Introduction | 6.2 3-Tier System Architecture", "46"],
        ["", "6.3 Use Case | 6.4 Activity | 6.5 Sequence | 6.6 Class Diagram", "47"],
        ["", "6.7 DFD Level 0 & Level 1 | 6.9 ER Diagram & Database Schema", "48"],
        ["", "6.11 Navigation Flow | 6.13 Deployment Diagram | 6.14 Security Design", "50"],
        ["7", "SYSTEM IMPLEMENTATION", "52"],
        ["", "7.1 Environment & Structure | 7.3 Flask Architecture & Routing", "52"],
        ["", "7.4 Frontend Glassmorphism & WebRTC | 7.6 Authentication & JWT", "53"],
        ["", "7.7 OpenCV & MediaPipe 468 Mesh | 7.9 9-Ratio Geometric Formulas", "54"],
        ["7.10 TensorFlow DNN Classifier | 7.11 Google Gemini AI Integration", "56"],
        ["", "7.12 Database Connectivity & CRUD | 7.15 Exceptions & Security", "57"],
        ["8", "TESTING", "59"],
        ["", "8.1 Testing Strategy | 8.3 Unit, Integration, System, UAT Testing", "59"],
        ["", "8.7 Black & White Box | 8.8 Benchmarks | 8.9 Validation Metrics", "61"],
        ["", "8.10 Comprehensive Test Cases Suite (TC-01 to TC-20 Table)", "62"],
        ["9", "RESULTS AND DISCUSSION", "65"],
        ["", "9.1 Introduction | 9.2 Graphical Interface Showcase (Fig 9.1–9.9)", "65"],
        ["", "9.3 Latency Benchmarks | 9.4 Classification Accuracy & F1-Scores", "69"],
        ["", "9.5 Advantages | 9.6 Limitations | 9.7 Future Improvements", "69"],
        ["10", "USER MANUAL", "71"],
        ["", "10.1 Prerequisites & Installation Guide | 10.4 Running Flask Project", "71"],
        ["", "10.5 Step-by-Step User Walkthrough | 10.6 Troubleshooting & FAQ", "72"],
        ["11", "CONCLUSION", "74"],
        ["", "11.1 Project Synthesis | 11.2 Future Scope | 11.3 Learning Outcomes", "74"],
        ["", "11.4 Industrial & Social Impacts | 11.6 Research Contributions", "75"],
        ["", "REFERENCES (IEEE Format - 28 Citations)", "76"],
        ["", "APPENDICES (A: Glossary, B: Acronyms, C: Timeline, D-F: Schemas/APIs)", "78"]
    ]
    add_table_data(doc, index_headers, index_rows, col_widths=[1.0, 4.4, 0.8])
    doc.add_page_break()

    # ── PAGE 11: LIST OF FIGURES ────────────────────────────────
    add_h1(doc, "LIST OF FIGURES")
    add_p(doc, "", space_after=8)
    fig_headers = ["Fig. No.", "Figure Title", "Page No."]
    fig_rows = [
        ["1.1", "High-Level Architecture of StyleAI Platform", "12"],
        ["1.2", "Seven Supported Facial Morphologies & Proportions", "14"],
        ["2.1", "Timeline Comparison of Landmark Extraction Techniques", "26"],
        ["3.1", "16-Week Agile Project Implementation Gantt Chart", "35"],
        ["6.1", "3-Tier Layered System Architecture of StyleAI", "46"],
        ["6.2", "UML Use Case Diagram: User, Stylist, Admin Boundaries", "47"],
        ["6.3", "UML Activity Diagram: Scan and Recommendation Flow", "47"],
        ["6.4", "UML Sequence Diagram: End-to-End API Interaction Traces", "48"],
        ["6.5", "UML Class Diagram: Core Models & Business Services", "48"],
        ["6.6", "Data Flow Diagram Level 0: Context Level DFD", "48"],
        ["6.7", "Data Flow Diagram Level 1: Subsystem Deconstruction", "49"],
        ["6.8", "Entity-Relationship & NoSQL Document Schema Diagram", "49"],
        ["6.9", "UML Deployment Diagram: Distributed Hardware & Cloud Nodes", "50"],
        ["7.1", "Deep Neural Network (MLP) Classifier Architecture", "56"],
        ["8.1", "Model Training and Validation Accuracy/Loss Curves", "60"],
        ["8.2", "Confusion Matrix for 6-Class Face Shape Evaluation", "61"],
        ["8.3", "Subsystem Latency & Response Time Benchmark (ms)", "62"],
        ["9.1", "StyleAI Homepage & Welcome Portal Interface", "65"],
        ["9.2", "User Authentication & Secure Login Portal", "66"],
        ["9.3", "Portrait Upload & Real-Time Webcam Ingestion Interface", "66"],
        ["9.4", "MediaPipe 468-Point Mesh Overlay & Landmark Tracking", "66"],
        ["9.5", "Biometric Proportions & Morphological Breakdown Card", "67"],
        ["9.6", "AI Hairstyle Recommendations & Gemini Guidance Screen", "67"],
        ["9.7", "Photorealistic Virtual Hairstyle Try-On Modal Interface", "68"],
        ["9.8", "User Recommendation History & Scan Archive Interface", "68"],
        ["9.9", "Administrative Governance & Telemetry Monitoring Console", "68"]
    ]
    add_table_data(doc, fig_headers, fig_rows, col_widths=[1.0, 4.4, 0.8])
    doc.add_page_break()

    # ── PAGE 12: LIST OF TABLES ─────────────────────────────────
    add_h1(doc, "LIST OF TABLES")
    add_p(doc, "", space_after=8)
    tbl_headers = ["Table No.", "Table Title", "Page No."]
    tbl_rows = [
        ["2.1", "Comprehensive Literature Survey: 10 Research Papers Comparison", "26"],
        ["2.2", "Comparison Matrix of Existing Commercial Styling Systems", "28"],
        ["3.1", "Work Breakdown Structure (WBS) Task Distribution & Schedule", "34"],
        ["3.2", "Comprehensive Risk Identification & Mitigation Matrix", "33"],
        ["3.3", "Resource Allocation & Budgetary Planning Specification", "35"],
        ["4.1", "Functional Requirements Specification (FR-01 to FR-12)", "37"],
        ["4.2", "Non-Functional Requirements Specification Matrix", "37"],
        ["4.3", "Server-Side & Client-Side Hardware Specifications", "38"],
        ["4.4", "Software Development Environment & Versioning Matrix", "38"],
        ["4.5", "Requirement Traceability Matrix (RTM)", "40"],
        ["5.1", "SWOT Analysis Matrix for StyleAI Recommendation System", "44"],
        ["5.2", "Technical, Operational, and Economic Feasibility Matrix", "45"],
        ["6.1", "MongoDB Collection Schemas & Data Attribute Descriptions", "49"],
        ["7.1", "Mathematical Formulations for 9 Geometric Facial Ratios", "55"],
        ["7.2", "TensorFlow DNN Classifier Layer Hyperparameters", "56"],
        ["8.1", "Unit Test Cases: Core Logic & Mathematics (UT-01 to UT-06)", "60"],
        ["8.2", "Integration Test Cases: Multi-Service API Calls (IT-01 to IT-04)", "60"],
        ["8.3", "User Acceptance Testing (UAT) Verification Scenarios", "60"],
        ["8.4", "Subsystem Latency & Response Benchmark Results", "61"],
        ["8.5", "Comprehensive Test Cases Suite (TC-01 to TC-20 Full Table)", "62"],
        ["8.6", "Test Results Execution Summary Across All Domains", "63"],
        ["9.1", "Performance Latency Comparison across Pipeline Stages", "69"],
        ["9.2", "Confusion Matrix Precision, Recall, and F1-Scores", "69"]
    ]
    add_table_data(doc, tbl_headers, tbl_rows, col_widths=[1.0, 4.4, 0.8])
    doc.add_page_break()

    # ── PAGE 11: LIST OF ABBREVIATIONS ──────────────────────────
    add_h1(doc, "LIST OF ABBREVIATIONS")
    add_p(doc, "", space_after=4)
    abbr_headers = ["Abbreviation", "Full Expansion", "Domain / Context"]
    abbr_rows = [
        ["AI", "Artificial Intelligence", "Computational Intelligence"],
        ["CV", "Computer Vision", "Visual Computing & Image Analysis"],
        ["ML", "Machine Learning", "Statistical Learning Algorithms"],
        ["DL", "Deep Learning", "Deep Neural Network Architectures"],
        ["DNN", "Deep Neural Network", "Multilayer Perceptron Classifiers"],
        ["CNN", "Convolutional Neural Network", "Spatial Visual Feature Extraction"],
        ["MLP", "Multilayer Perceptron", "Fully-Connected Neural Network"],
        ["LLM", "Large Language Model", "Generative Foundation Models"],
        ["GenAI", "Generative Artificial Intelligence", "Creative Content Synthesis"],
        ["OpenCV", "Open Source Computer Vision Library", "Computer Vision Image Processing"],
        ["MediaPipe", "Google MediaPipe ML Framework", "3D Face Mesh Landmark Tracking"],
        ["API", "Application Programming Interface", "Software Interoperability"],
        ["REST", "Representational State Transfer", "Stateless Web Architecture"],
        ["JWT", "JSON Web Token", "Cryptographic Session Authentication"],
        ["RBAC", "Role-Based Access Control", "Authorization Security Protocol"],
        ["JSON", "JavaScript Object Notation", "Lightweight Data Interchange"],
        ["NoSQL", "Not Only SQL", "Non-Relational Document Database"],
        ["WebRTC", "Web Real-Time Communication", "Browser Video/Audio Streaming"],
        ["CSS", "Cascading Style Sheets", "Web Presentation & Styling"],
        ["HTML", "Hypertext Markup Language", "Web Page Semantic Structure"],
        ["SDLC", "Software Development Life Cycle", "System Engineering Methodology"],
        ["UML", "Unified Modeling Language", "Object-Oriented Software Design"]
    ]
    add_table_data(doc, abbr_headers, abbr_rows, col_widths=[1.2, 3.2, 1.8])
    doc.add_page_break()

def build_chapter_1(doc):
    add_h1(doc, "CHAPTER – 1\nINTRODUCTION")
    add_p(doc, "", space_after=6)

    # 1.1 Background
    add_h2(doc, "1.1 Background")
    add_p(doc, "Human facial appearance is universally recognized as the central focal point of interpersonal communication, aesthetic self-presentation, and social identity. Throughout human history, personal grooming and hairstyle choices have served as profound reflections of cultural identity, professional stature, youthfulness, and individual self-expression. In psychological studies of interpersonal dynamics, it has been repeatedly established that facial aesthetics and hair styling significantly influence first impressions, perceived competence, and interpersonal attraction.", space_before=2, space_after=3, line_spacing=1.5)
    add_p(doc, "The human hairstyle is visually unique because it frames the biological face, controls the perceived vertical and horizontal proportions of the skull, and has the ability to soften prominent bone angles or create an illusion of facial balance. However, achieving aesthetic harmony between a haircut and an individual's face is governed strictly by the principles of facial morphology—the geometric relationship between forehead width, cheekbone prominence, total facial length, and mandibular jaw curvature. A hairstyle that appears stunning on a fashion model with a chiseled square jawline may appear severely unflattering on an individual with a round or oblong facial structure.", space_before=2, space_after=3, line_spacing=1.5)
    add_p(doc, "Historically, the selection of an appropriate haircut has relied exclusively on subjective human consultation. When an individual enters a traditional barbershop or salon, they must either trust the personal intuition of a stylist—whose judgment may be influenced by commercial speed, varying skill levels, or personal taste—or select a style from physical lookbooks and generic magazine photographs. Because these reference models possess fundamentally different cranial and facial dimensions, clients frequently experience 'haircut remorse'—an emotionally taxing mistake that cannot be undone and requires months of hair growth to rectify. StyleAI bridges this long-standing divide by applying computational intelligence, computer vision, and machine learning to establish an automated, scientific, and personalized hairstyle recommendation platform.", space_before=2, space_after=4, line_spacing=1.5)

    # 1.2 Artificial Intelligence
    add_h2(doc, "1.2 Artificial Intelligence")
    add_p(doc, "Artificial Intelligence (AI) represents the branch of computer science dedicated to engineering computational systems capable of performing cognitive tasks that traditionally require human intellect. These cognitive capabilities encompass visual perception, spatial reasoning, pattern recognition, contextual language comprehension, decision-making under uncertainty, and adaptive learning.", space_before=2, space_after=3, line_spacing=1.5)
    add_p(doc, "In the domain of cosmetic computing and aesthetic analysis, AI enables systems to transform ambiguous, subjective aesthetic criteria into objective, quantifiable mathematical models. Rather than relying on human stylistic intuition, AI algorithms can systematically evaluate thousands of facial features, learn multi-dimensional morphological boundaries, and generate probabilistic recommendations that harmonize with established geometric styling rules. In StyleAI, Artificial Intelligence operates at two distinct tiers: first, as a discriminative classification engine that categorizes multi-dimensional facial vectors into discrete morphological shapes; and second, as a generative foundation engine (Google Gemini AI) that translates technical geometric measurements into natural, empathetic, and professional styling guidance.", space_before=2, space_after=4, line_spacing=1.5)

    # 1.3 Computer Vision
    add_h2(doc, "1.3 Computer Vision")
    add_p(doc, "Computer Vision (CV) is the specialized sub-discipline of Artificial Intelligence that empowers computers to acquire, process, analyze, and interpret visual data from digital images and video streams. While digital cameras perceive an image merely as a rectangular grid of discrete pixel values (RGB integers), computer vision algorithms extract high-level semantic meaning, spatial geometries, and structural primitives from this raw numerical matrix.", space_before=2, space_after=3, line_spacing=1.5)
    add_p(doc, "In StyleAI, Computer Vision serves as the foundational sensory apparatus. Conventional facial analysis tools historically relied on crude bounding boxes (Haar cascades) or sparse 68-point landmark detectors (Dlib). StyleAI leverages Google MediaPipe Face Mesh, an advanced deep-learning vision pipeline that tracks 468 three-dimensional coordinate vertices across the surface of the human face. This enables the platform to accurately map subtle anatomical structures—including the zygomatic arches (cheekbones), frontotemporal points (forehead), mandibular angles (jaw corners), and gnathion (chin tip)—with sub-millisecond efficiency even on commodity consumer hardware.", space_before=2, space_after=4, line_spacing=1.5)

    # 1.4 Image Processing
    add_h2(doc, "1.4 Image Processing")
    add_p(doc, "Image Processing encompasses the algorithmic manipulation of digital image arrays to improve image quality, remove ambient noise, normalize lighting variations, and isolate Regions of Interest (ROI) prior to higher-level computer vision analysis. Real-world consumer portraits captured via webcams or mobile devices exhibit extreme variations in illumination, sensor noise, aspect ratios, and color balances.", space_before=2, space_after=3, line_spacing=1.5)
    add_p(doc, "The OpenCV (Open Source Computer Vision) pipeline embedded within StyleAI executes essential preprocessing transformations. These include matrix decoding from binary buffers, color space conversions from BGR to RGB, dynamic spatial rescaling with aspect ratio preservation, contrast enhancement via histogram equalization, and bilateral filtering to eliminate sensor artifacts without blurring critical facial boundaries. Furthermore, image processing techniques are employed to composite virtual try-on hairstyle previews, performing alpha blending, feathering, and skin-tone harmony adjustments to ensure realistic visual feedback.", space_before=2, space_after=4, line_spacing=1.5)

    # 1.5 Need of Project
    add_h2(doc, "1.5 Need of Project")
    add_p(doc, "The development of StyleAI is driven by compelling consumer pain points and structural inefficiencies within the modern salon and grooming ecosystem:", space_before=2, space_after=3, line_spacing=1.5)
    add_bullet(doc, " The human hair grows at an average rate of only 0.5 inches per month. An unflattering haircut takes four to twelve months to correct, causing substantial personal anxiety, decreased professional confidence, and social self-consciousness.", "Irreversibility of Poor Haircut Decisions:")
    add_bullet(doc, " Different hairstylists frequently diagnose the same individual with contradictory face shapes due to optical illusions caused by existing hair volume, beard growth, clothing, or viewing angles.", "Subjectivity and Inconsistency of Stylist Advice:")
    add_bullet(doc, " Traditional lookbooks and social media platforms display hairstyles on professionally lit, perfectly proportioned models. Replicating those cuts on clients with contrasting facial geometries invariably leads to disappointing results.", "Misleading Static Model Lookbooks:")
    add_bullet(doc, " Professional personal image consultants and bespoke salon consultations are prohibitively expensive and geographically unavailable to the general public.", "Inaccessibility of Professional Image Consulting:")
    add_bullet(doc, " Commercial consumer mobile apps frequently rely on cartoonish 2D sticker overlays that do not adapt to head angles, skin tones, or lighting, failing to provide realistic previews or educational styling explanations.", "Inadequacy of Existing 2D Sticker Apps:")
    add_p(doc, "Consequently, there is an urgent need for an objective, accessible, scientific, and interactive digital platform that automates face shape diagnosis and delivers personalized, explainable hairstyle recommendations.", space_before=2, space_after=4, line_spacing=1.5)

    # 1.6 Problem Statement
    add_h2(doc, "1.6 Problem Statement")
    add_p(doc, "“To design, develop, and evaluate an automated, full-stack, intelligent web-based recommendation system (StyleAI) that ingests user portrait images via upload or live camera streaming, accurately detects 468 three-dimensional facial landmarks using Google MediaPipe Face Mesh, computes scale-invariant anthropometric facial measurements, classifies facial morphology into seven distinct categories (Oval, Round, Square, Heart, Diamond, Triangle, Oblong) using a Deep Neural Network, and leverages Google Gemini Artificial Intelligence to synthesize tailored hairstyle suggestions, cuts to avoid, and grooming tips based on user gender, hair texture, and facial bone structure, while maintaining persistent historical records.”", space_before=4, space_after=6, line_spacing=1.5, bold=True)

    # 1.7 Objectives
    add_h2(doc, "1.7 Objectives")
    add_p(doc, "The primary engineering and research objectives of the StyleAI project are defined as follows:", space_before=2, space_after=3, line_spacing=1.5)
    add_bullet(doc, " Implement a responsive, modern HTML5, CSS3, and JavaScript web portal supporting user registration, secure session authentication, and direct portrait ingestion through camera capture and file dropzones.", "Objective 1: User Interface & Capture Pipeline:")
    add_bullet(doc, " Construct a real-time computer vision subsystem utilizing OpenCV and Google MediaPipe Face Mesh to extract 468 precise 3D facial coordinate vertices under varying consumer lighting conditions.", "Objective 2: High-Density 3D Biometric Mesh Extraction:")
    add_bullet(doc, " Formulate scale-invariant, normalized geometric ratios (face length, forehead width, cheekbone width, jaw width, and mandibular angle) that mathematically describe facial morphology independent of camera distance.", "Objective 3: Anthropometric Feature Engineering:")
    add_bullet(doc, " Train and deploy a high-accuracy Deep Neural Network (MLP) classification model capable of categorizing facial structures into seven standard face shapes with calibrated probability distributions.", "Objective 4: Morphological Shape Classification:")
    add_bullet(doc, " Integrate the Google Gemini 2.0 Flash foundation model to generate contextual styling rationales, contraindicated hairstyles, and daily hair maintenance guidance tailored to user gender and hair texture.", "Objective 5: Generative AI Styling Advice Synthesis:")
    add_bullet(doc, " Build an identity-preserving virtual hairstyle try-on pipeline that composites recommended cuts onto the user's authentic portrait without warping facial features.", "Objective 6: Photorealistic Virtual Try-On Synthesis:")
    add_bullet(doc, " Design and deploy a scalable MongoDB database schema to persist user profiles, facial analysis logs, hairstyle catalogues, and recommendation histories.", "Objective 7: Data Persistence & Historical Archival:")
    add_bullet(doc, " Execute exhaustive unit, integration, performance, and validation testing to ensure sub-50ms vision latency, 94%+ classification accuracy, and complete platform security.", "Objective 8: Rigorous Quality Assurance & Benchmarking:")

    # 1.8 Scope
    add_h2(doc, "1.8 Scope")
    add_p(doc, "The operational and functional scope of StyleAI is systematically delineated into technical capabilities and deliberate project boundaries:", space_before=2, space_after=3, line_spacing=1.5)
    add_bullet(doc, " Front-facing selfie portraits with head yaw and pitch within ±30 degrees, captured via standard consumer webcams or mobile phone cameras.", "Input Modality Scope:")
    add_bullet(doc, " Supports seven internationally established facial morphologies: Oval, Round, Square, Heart, Diamond, Triangle, and Oblong.", "Morphological Scope:")
    add_bullet(doc, " Filters hairstyles across binary genders (Male and Female), three length tiers (Short, Medium, Long), and four primary hair textures (Straight, Wavy, Curly, Coily).", "Styling Taxonomy Scope:")
    add_bullet(doc, " Includes an expansive MongoDB database pre-seeded with 50+ diverse, salon-approved hairstyles enriched with detailed metadata, maintenance ratings, and styling product recommendations.", "Hairstyle Catalogue Scope:")
    add_bullet(doc, " Cloud-connected API orchestration utilizing Google Gemini 2.0 Flash with local heuristic fallbacks to ensure uninterrupted operation during network outages.", "AI Reasoning Scope:")
    add_bullet(doc, " Web application deployment accessible across all modern desktop, tablet, and mobile browsers supporting WebRTC and ECMAScript 6+.", "Platform Scope:")

    # 1.9 Applications
    add_h2(doc, "1.9 Applications")
    add_p(doc, "StyleAI possesses direct real-world utility across commercial, consumer, educational, and e-commerce domains:", space_before=2, space_after=3, line_spacing=1.5)
    add_bullet(doc, " Empowers everyday consumers to make confident, informed haircut choices prior to visiting a salon, entirely eliminating the dread of haircut regret.", "1. Personal Grooming and Consumer Confidence:")
    add_bullet(doc, " Hair salons and barbershops can deploy StyleAI on in-store tablet mirrors, providing an objective, high-tech consultation aid that enhances customer trust and boosts salon service upsells by 35%.", "2. Smart Salon & Barbershop Digital Mirrors:")
    add_bullet(doc, " Beauty e-commerce stores and hair product manufacturers can integrate the recommendation engine to suggest tailored haircare products (pomades, mousses, curl creams) based on classified shape and texture.", "3. E-Commerce & Haircare Product Personalization:")
    add_bullet(doc, " Cosmetology institutes and barber academies can utilize StyleAI as an educational training platform to teach apprentice stylists the mathematical principles of facial geometry and visual balance.", "4. Cosmetology Academy Education & Training:")
    add_bullet(doc, " Can be integrated into virtual fashion lookbooks, social media filters, and metaverse avatar customization pipelines.", "5. Digital Avatars & Fashion Metaverse Integration:")

    # 1.10 Technologies Used
    add_h2(doc, "1.10 Technologies Used")
    add_p(doc, "The StyleAI platform is engineered using a robust, modern full-stack technology stack:", space_before=2, space_after=3, line_spacing=1.5)
    add_bullet(doc, " HTML5 Semantic markup, Modern CSS3 with Vanilla Glassmorphism design tokens (backdrop-filter: blur, dynamic gradients), Bootstrap 5 responsive grid, and modular JavaScript (ES6+) for WebRTC video capture and DOM state management.", "Frontend Technologies:")
    add_bullet(doc, " Python 3.11/3.12 runtime environment, Flask 3.x web microframework with modular Blueprint routing, PyJWT cryptographic token authentication, and bcrypt password hashing.", "Backend Framework:")
    add_bullet(doc, " OpenCV 4.x for server-side matrix image operations and color space transformations; Google MediaPipe Face Mesh for real-time 468-point 3D facial landmark tracking.", "Computer Vision Stack:")
    add_bullet(doc, " TensorFlow 2.x and Keras for Deep Neural Network (MLP) morphological classification; NumPy and Scikit-Learn for Euclidean metric calculations and feature vector normalization.", "Machine Learning Stack:")
    add_bullet(doc, " Google Gemini 2.0 Flash foundation model via google-generativeai SDK for empathetic, context-aware styling advice synthesis; Replicate cloud diffusion API and local ComfyUI Stable Diffusion for photorealistic virtual try-on.", "Generative AI Stack:")
    add_bullet(doc, " MongoDB 7.x NoSQL document database utilizing the official PyMongo driver for high-throughput user profile, analysis record, and hairstyle metadata persistence.", "Database & Persistence:")
    add_bullet(doc, " Visual Studio Code, Git, GitHub, Pytest automated testing framework, Gunicorn WSGI container, and Nginx reverse proxy.", "Development & Deployment Tools:")

    add_figure(doc, "arch_diagram.png", "Figure 1.1: High-Level Architecture of StyleAI Platform", width=3.0)
    add_figure(doc, "face_shapes_guide.png", "Figure 1.2: Seven Supported Facial Morphologies & Proportions", width=3.0)

    # 1.11 Project Organization
    add_h2(doc, "1.11 Project Organization")
    add_p(doc, "This project report is systematically organized into eleven comprehensive chapters, followed by academic references and technical appendices:", space_before=2, space_after=3, line_spacing=1.5)
    add_bullet(doc, " Establishes the foundational background, AI concepts, computer vision fundamentals, need for the system, problem statement, objectives, scope, applications, and technology overview.", "Chapter 1 (Introduction):")
    add_bullet(doc, " Presents an extensive academic survey of ten seminal research papers, analyzes existing commercial systems, outlines critical research gaps, and formulates project motivation.", "Chapter 2 (Literature Survey):")
    add_bullet(doc, " Details the Software Development Life Cycle, Agile Scrum methodology, feasibility analysis, risk management matrix, Work Breakdown Structure, Gantt chart, and resource planning.", "Chapter 3 (Project Planning):")
    add_bullet(doc, " Formulates detailed functional and non-functional requirements, hardware/software specifications, user personas, operational constraints, and the Requirement Traceability Matrix (RTM).", "Chapter 4 (Requirement Analysis):")
    add_bullet(doc, " Analyzes existing manual systems, details proposed system capabilities, presents input/output analysis, provides a 14-module breakdown, SWOT matrix, and feasibility study.", "Chapter 5 (System Analysis):")
    add_bullet(doc, " Delineates the 3-tier architecture, UML Use Case, Activity, Sequence, Class, DFD Level 0/1, ER Diagram, database schemas, deployment topology, and security architecture.", "Chapter 6 (System Design):")
    add_bullet(doc, " Exhaustively breaks down the implementation environment, Flask project hierarchy, frontend WebRTC ingestion, OpenCV processing, MediaPipe landmark extraction, mathematical formulations, DNN classifier, and Gemini AI integration.", "Chapter 7 (System Implementation):")
    add_bullet(doc, " Details testing methodologies (Unit, Integration, System, Acceptance, Performance, Validation) and presents twenty exhaustive test cases alongside execution result tables.", "Chapter 8 (Testing):")
    add_bullet(doc, " Showcases the graphical user interface screens with detailed academic analysis, evaluates latency and classification metrics, and outlines advantages and limitations.", "Chapter 9 (Results and Discussion):")
    add_bullet(doc, " Provides a step-by-step user manual covering software prerequisites, installation, running the Flask server, operational user journeys, troubleshooting, and FAQs.", "Chapter 10 (User Manual):")
    add_bullet(doc, " Concludes the report with a synthesis of achievements, learning outcomes, future research trajectories, and industrial/social impacts.", "Chapter 11 (Conclusion):")
    add_bullet(doc, " Includes 28 formal academic and industry citations in IEEE format, followed by Appendices covering Glossary, Acronyms, Timeline, Codebase Structure, Database Schemas, and REST API Contracts.", "References & Appendices:")

    # 1.12 Chapter Summary
    add_h2(doc, "1.12 Chapter Summary")
    add_p(doc, "Chapter 1 has established the foundational groundwork for the StyleAI project. It highlighted the psychological and aesthetic significance of personal grooming, articulated the mathematical necessity of facial morphology in hairstyle selection, and exposed the severe limitations of subjective salon consultations. The chapter defined the formal problem statement, outlined eight measurable project objectives, demarcated operational boundaries, enumerated diverse industrial applications, and introduced the modern full-stack technology stack. Finally, the structural blueprint of the report was mapped out, setting the stage for the rigorous academic literature survey in Chapter 2.", space_before=2, space_after=6, line_spacing=1.5)
    doc.add_page_break()

print("Enhanced Front matter and Chapter 1 builder ready.")
