"""
Report Builder Part 3:
- Chapter 4: Requirement Analysis (Functional, Non-Functional, Hardware/Software, User, Constraints, RTM, Flow, Summary)
- Chapter 5: System Analysis (Existing system, Problems, Limitations, Proposed system, Advantages, Input/Output, 14 Modules, SWOT, Feasibility, Summary)
- Chapter 6: System Design (Architecture, Use Case, Activity, Sequence, Class, DFD0, DFD1, ERD, DB Design, Nav Flow, Workflow, Deployment, Security, Summary)
"""

import os
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from scripts.report_helpers import (
    add_p, add_bullet, add_h1, add_h2, add_h3,
    add_table_data, add_figure, add_code_block, ASSETS_DIR
)

def build_chapter_4(doc):
    add_h1(doc, "CHAPTER – 4\nREQUIREMENT ANALYSIS")
    add_p(doc, "", space_after=6)

    # 4.1 Introduction
    add_h2(doc, "4.1 Introduction")
    add_p(doc, "Requirement Analysis constitutes the foundational phase of software engineering where user expectations, operational constraints, system behaviors, and environmental interfaces are systematically discovered, analyzed, specified, and validated. In a computer vision and artificial intelligence application, requirement analysis is particularly vital because it bridges the subjective human domain of personal aesthetics with the rigorous, deterministic mathematical realm of landmark geometry and classification probabilities.", space_before=4, space_after=6, line_spacing=1.5)
    add_p(doc, "This chapter specifies the complete functional and non-functional requirements of StyleAI, defines hardware and software operational requirements, characterizes user personas, formalizes technical constraints, presents the Requirement Traceability Matrix (RTM), and maps the end-to-end requirement flow.", space_before=4, space_after=10, line_spacing=1.5)

    # 4.2 Functional Requirements
    add_h2(doc, "4.2 Functional Requirements")
    add_p(doc, "Functional requirements define the specific operational behaviors, computations, data transformations, and services that the StyleAI platform must execute. Twelve core functional requirements (FR-01 to FR-12) are formalized in Table 4.1:", space_before=4, space_after=6, line_spacing=1.5)

    fr_headers = ["Req ID", "Functional Requirement Description", "Trigger / Input Data", "System Processing & Transformation", "Output / System Action"]
    fr_rows = [
        ["FR-01", "User Registration & Cryptographic Hashing", "Name, Email, Password, Gender, Texture", "Validates input schemas, salts password with bcrypt (12 rounds), stores in MongoDB", "201 Created JSON response with user profile ID"],
        ["FR-02", "JWT Session Authentication & RBAC Guard", "Email and plaintext Password", "Verifies bcrypt hash, signs HMAC-SHA256 JWT bearer token containing role and user_id", "200 OK with JWT token and auth redirect"],
        ["FR-03", "Live WebRTC Camera Stream & Canvas Capture", "Client grants navigator.mediaDevices permission", "Streams 30 FPS video feed onto HTML5 canvas with dynamic oval alignment guide", "High-res portrait snapshot buffer (JPEG/PNG)"],
        ["FR-04", "Direct High-Resolution File Upload", "User drops portrait file (< 10 MB)", "Validates MIME type, performs sanitization, enforces size boundary checks", "Stored securely in server uploads directory"],
        ["FR-05", "OpenCV Matrix Preprocessing", "Uploaded image buffer", "Decodes buffer, transforms BGR to RGB, normalizes aspect ratio, applies histogram balance", "Clean normalized 3-channel matrix"],
        ["FR-06", "MediaPipe 468-Point 3D Mesh Extraction", "Normalized RGB image matrix", "Executes BlazeFace detector and 3D mesh regressor, extracts 468 (x,y,z) spatial vertices", "Array of 468 3D landmark coordinate tuples"],
        ["FR-07", "Anthropometric Feature Ratio Calculation", "Landmark coordinate array", "Computes Euclidean distances across 9 key anatomical points (jaw, zygoma, forehead, chin)", "9-dimensional normalized feature vector"],
        ["FR-08", "Deep Neural Network Shape Classification", "9-dimensional feature vector", "Feeds vector to trained Keras MLP model, evaluates dense layers, applies Softmax", "Classified face shape + 7-class probabilities"],
        ["FR-09", "Multi-Attribute Hairstyle Catalog Query", "Detected shape + Gender + Hair texture", "Queries MongoDB hairstyles collection, ranks styles matching shape and texture affinity", "Structured list of top-ranked haircut cards"],
        ["FR-10", "Google Gemini AI Generative Advice", "Shape, gender, texture + prompt payload", "Calls Gemini 2.0 Flash API via google-genai SDK, requests structured JSON styling schema", "Styling rationales, cuts to avoid, grooming tips"],
        ["FR-11", "Identity-Preserving Virtual Try-On", "User portrait + Selected hairstyle ID", "Generates cranial hair mask, triggers diffusion inpainting, composites hair over skull", "Photorealistic try-on preview composite"],
        ["FR-12", "Historical Session Archival & Management", "Analysis ID, token, user profile", "Inserts scan record into MongoDB analyses collection; enables retrieval and deletion", "Persistent chronological history cards"]
    ]
    add_table_data(doc, fr_headers, fr_rows, col_widths=[0.7, 1.6, 1.3, 1.9, 1.7],
                   caption="Table 4.1: Functional Requirements Specification (FR-01 to FR-12)")

    # 4.3 Non-Functional Requirements
    add_h2(doc, "4.3 Non-Functional Requirements")
    add_p(doc, "Non-functional requirements specify the architectural qualities, operational performance thresholds, security constraints, and usability criteria governing the system:", space_before=4, space_after=6, line_spacing=1.5)

    nfr_headers = ["NFR ID", "Quality Dimension", "Target Benchmark / Criterion", "Architectural Implementation Strategy"]
    nfr_rows = [
        ["NFR-01", "Performance Latency", "Landmark extraction < 50ms; DNN classification < 20ms", "Vectorized NumPy calculations and lightweight CPU-optimized MediaPipe models"],
        ["NFR-02", "End-to-End Throughput", "Total analysis API response time < 600ms (excl. Gemini)", "Non-blocking Flask routing with concurrent thread worker pools in Gunicorn"],
        ["NFR-03", "System Reliability & Uptime", "99.5% operational availability with graceful fallbacks", "Local rule-based heuristic advisor automatically activated if Gemini API fails"],
        ["NFR-04", "Security & Data Privacy", "Zero plain-text password storage; zero ID distortion", "Bcrypt hashing with work factor 12; PyJWT token verification; CORS headers"],
        ["NFR-05", "Usability & Accessibility", "Clean Glassmorphism interface; sub-3-second user journey", "Mobile-first responsive CSS Grid/Flexbox with clear visual guidance overlays"],
        ["NFR-06", "Maintainability & Code Health", "100% automated test pass rate with modular architecture", "Clean separation into routes, services, models, and ML pipelines; 103 Pytest cases"]
    ]
    add_table_data(doc, nfr_headers, nfr_rows, col_widths=[0.8, 1.5, 2.3, 2.6],
                   caption="Table 4.2: Non-Functional Requirements Specification Matrix")

    # 4.4 Hardware Requirements
    add_h2(doc, "4.4 Hardware Requirements")
    add_p(doc, "The execution environment requires specific hardware configurations across server-side application hosting and client-side web browser interaction:", space_before=4, space_after=6, line_spacing=1.5)

    hw_headers = ["System Tier", "Hardware Component", "Minimum Specification", "Recommended Specification"]
    hw_rows = [
        ["Server-Side", "Processor (CPU)", "Dual-Core 2.0 GHz x86-64", "Intel Core i7 / AMD Ryzen 7 (8 Cores)"],
        ["Server-Side", "System Memory (RAM)", "4 GB DDR4", "16 GB DDR4 / DDR5 High-Speed RAM"],
        ["Server-Side", "Storage (Disk)", "10 GB Available SSD Space", "50 GB NVMe M.2 Solid State Drive"],
        ["Server-Side", "Network Connectivity", "10 Mbps Broadband", "100 Mbps Dedicated Full-Duplex Uplink"],
        ["Client-Side", "Device Platform", "Mobile / Tablet / PC", "Standard Desktop PC or Modern Smartphone"],
        ["Client-Side", "Camera Hardware", "VGA Webcam (640x480 @ 15 FPS)", "Full HD 1080p Webcam @ 30 FPS"],
        ["Client-Side", "Display Resolution", "1024 x 768 Pixels", "1920 x 1080 (Full HD) IPS Display"]
    ]
    add_table_data(doc, hw_headers, hw_rows, col_widths=[1.2, 1.8, 2.1, 2.1],
                   caption="Table 4.3: Server-Side and Client-Side Hardware Specifications")

    # 4.5 Software Requirements
    add_h2(doc, "4.5 Software Requirements")
    add_p(doc, "The software stack incorporates contemporary open-source runtimes, libraries, frameworks, and database engines:", space_before=4, space_after=6, line_spacing=1.5)

    sw_headers = ["Software Layer", "Technology Component", "Version Deployed", "Functional Role in StyleAI"]
    sw_rows = [
        ["Operating System", "Microsoft Windows 10/11 / Linux Ubuntu 22.04 LTS", "64-bit", "Host operating system for server runtime and development"],
        ["Runtime Environment", "Python Runtime", "3.11.x / 3.12.x", "Core programming runtime for backend and ML pipeline"],
        ["Web Framework", "Flask WSGI Microframework", "3.0.x", "RESTful API routing, Blueprint controllers, JSON responses"],
        ["Computer Vision", "OpenCV (opencv-python)", "4.9.x", "Matrix transformations, BGR/RGB conversion, image blending"],
        ["Biometric Tracking", "Google MediaPipe", "0.10.x", "468-point 3D facial landmark mesh localization"],
        ["Machine Learning", "TensorFlow & Keras / Scikit-Learn", "2.15.x / 1.4.x", "Deep Neural Network MLP classifier and dataset scaling"],
        ["Foundation AI Model", "Google Gemini 2.0 Flash (google-genai)", "Official SDK", "Contextual generative styling advice and grooming synthesis"],
        ["Database Engine", "MongoDB Community Server", "7.0.x", "NoSQL document persistence for users, styles, and scans"],
        ["Frontend Presentation", "HTML5, CSS3 Glassmorphism, Bootstrap 5, JS", "ES6+ Native", "Responsive browser user interface and WebRTC streaming"],
        ["Testing Framework", "Pytest & Coverage.py", "8.1.x", "Automated unit, integration, and security test harnesses"]
    ]
    add_table_data(doc, sw_headers, sw_rows, col_widths=[1.4, 2.0, 1.1, 2.7],
                   caption="Table 4.4: Software Development Environment and Versioning Matrix")

    # 4.6 User Requirements
    add_h2(doc, "4.6 User Requirements & Target Personas")
    add_p(doc, "StyleAI is architected around three target user personas, each with distinct interaction goals:", space_before=4, space_after=6, line_spacing=1.5)
    add_bullet(doc, " Needs an intuitive, non-intimidating tool to discover their true face shape within seconds. Requires plain-English explanations of why specific cuts work, visual examples, cuts to avoid, and the ability to save preferred styles for their next salon visit.", "Persona 1: Everyday Consumer (Client):")
    add_bullet(doc, " Uses StyleAI on a tablet at the salon chair to provide objective consultation to indecisive clients. Demands transparent facial measurements, rapid lookbook filtering by hair texture, and realistic virtual try-on previews to convince clients before cutting.", "Persona 2: Professional Hair Stylist & Barber:")
    add_bullet(doc, " Requires an administrative dashboard to manage user roles, audit hairstyle metadata catalog items, monitor server response latencies, and verify external AI API quotas.", "Persona 3: System Administrator:")

    # 4.7 Constraints
    add_h2(doc, "4.7 Operational Constraints & Boundaries")
    add_p(doc, "The operation of StyleAI is bounded by several unavoidable physical, biological, and technical constraints:", space_before=4, space_after=6, line_spacing=1.5)
    add_bullet(doc, " MediaPipe relies on visible lighting contrast. Severe underexposure (< 15 lux) or intense backlighting impairs landmark accuracy.", "1. Illumination Constraints:")
    add_bullet(doc, " The mathematical ratio formulas assume near-orthographic projection. Head rotation exceeding ±30 degrees yaw or pitch distorts width-to-length calculations.", "2. Pose Constraints:")
    add_bullet(doc, " Extremely dense full-face beards, thick bangs covering the entire forehead, or oversized sunglasses occlude anatomical landmarks (gnathion, trichion, zygoma), reducing jawline confidence.", "3. Occlusion Constraints:")
    add_bullet(doc, " Generative advice depends on active internet connectivity to query Google Gemini 2.0 Flash; offline environments trigger rule-based fallback advice.", "4. Cloud API Availability:")

    # 4.8 Requirement Traceability Matrix (RTM)
    add_h2(doc, "4.8 Requirement Traceability Matrix (RTM)")
    add_p(doc, "The Requirement Traceability Matrix (RTM) establishes bi-directional verification between user needs, functional requirements, architectural modules, and automated test cases:", space_before=4, space_after=6, line_spacing=1.5)

    rtm_headers = ["User Need", "Functional Req", "Architectural Module", "Design Diagram", "Test Case ID"]
    rtm_rows = [
        ["Secure personal access", "FR-01, FR-02", "server/services/auth_service.py", "Class Diagram (UserModel)", "UT-01, SEC-01"],
        ["Capture face image easily", "FR-03, FR-04", "client/js/camera.js", "Activity Diagram (Capture)", "UI-01, IT-01"],
        ["Detect face shape accurately", "FR-06, FR-07, FR-08", "ml/feature_extractor.py, model.py", "DNN Architecture (Fig 7.1)", "UT-02, UT-03, UT-04"],
        ["Get personalized hairstyles", "FR-09", "server/services/recommendation.py", "ER Diagram (Hairstyles)", "IT-02, API-03"],
        ["Understand styling rationale", "FR-10", "server/services/genai_service.py", "Sequence Diagram (Fig 6.4)", "IT-03, API-04"],
        ["Visualize haircut on selfie", "FR-11", "server/services/tryon_service.py", "Deployment Diagram (Fig 6.9)", "IT-04, PT-05"],
        ["Inspect historical scans", "FR-12", "server/routes/analysis.py", "DFD Level 1 (Store D3)", "API-05, UAT-02"]
    ]
    add_table_data(doc, rtm_headers, rtm_rows, col_widths=[1.5, 1.2, 2.0, 1.5, 1.0],
                   caption="Table 4.5: Requirement Traceability Matrix (RTM)")

    # 4.9 Requirement Flow
    add_h2(doc, "4.9 Requirement Flow Architecture")
    add_p(doc, "The requirement flow follows a disciplined computational pipeline: Portrait Acquisition -> Biometric Normalization -> Landmark Mesh Extraction -> Geometric Ratio Formulation -> Deep Neural Classification -> Contextual Knowledge Querying -> Generative Advice Synthesis -> Photorealistic Try-On Compositing -> Persistent Storage.", space_before=4, space_after=10, line_spacing=1.5)

    # 4.10 Chapter Summary
    add_h2(doc, "4.10 Chapter Summary")
    add_p(doc, "Chapter 4 provided an exhaustive requirement engineering specification for StyleAI. It detailed twelve functional requirements, tabulated six non-functional quality dimensions, defined hardware and software operational requirements, characterized user personas, and documented environmental constraints. The Requirement Traceability Matrix confirmed complete coverage between user needs and automated verification suites. Chapter 5 builds upon these requirements to present the detailed System Analysis.", space_before=4, space_after=12, line_spacing=1.5)
    doc.add_page_break()

def build_chapter_5(doc):
    add_h1(doc, "CHAPTER – 5\nSYSTEM ANALYSIS")
    add_p(doc, "", space_after=6)

    # 5.1 Introduction
    add_h2(doc, "5.1 Introduction")
    add_p(doc, "System Analysis is the process of examining an existing operational problem, deconstructing its inefficiencies, and defining the precise logical and technical capabilities required of a replacement system. In the context of personal styling, system analysis requires scrutinizing how haircuts are currently decided in commercial salons and identifying why conventional methods fail both clients and practitioners.", space_before=4, space_after=6, line_spacing=1.5)
    add_p(doc, "This chapter examines the existing manual salon workflow, exposes its flaws and commercial limitations, presents the proposed StyleAI solution philosophy, conducts input and output data analyses, performs an in-depth breakdown of all fourteen project modules, evaluates the platform via a SWOT analysis, and conducts a rigorous feasibility analysis.", space_before=4, space_after=10, line_spacing=1.5)

    # 5.2 Existing System
    add_h2(doc, "5.2 Study of Current Conventional Systems")
    add_p(doc, "The current ecosystem of haircut consultation operates almost identically to how it functioned five decades ago. The traditional consultation procedure consists of the following steps:", space_before=4, space_after=6, line_spacing=1.5)
    add_bullet(doc, " The client enters the barbershop and sits in the chair. The stylist looks at the mirror and conducts a 10-second visual appraisal of the client's head, mentally categorizing it as 'round', 'long', or 'square'.", "1. Subjective Mirror Inspection:")
    add_bullet(doc, " The client is handed a physical glossy magazine or asked to show an Instagram photo of a celebrity whose haircut they admire.", "2. Model Lookbook Browsing:")
    add_bullet(doc, " The stylist cuts the client's hair to match the photograph, without adjusting the cut for the client's different bone structure or hair texture.", "3. Blind Scissor Execution:")
    add_bullet(doc, " The client looks in the mirror with disappointment when the haircut does not suit their face shape, but the damage is irreversible.", "4. Post-Cut Realization:")

    # 5.3 Problems
    add_h2(doc, "5.3 Problems and Weaknesses of Current Systems")
    add_p(doc, "Rigorous analysis reveals six critical weaknesses in the existing paradigm:", space_before=4, space_after=6, line_spacing=1.5)
    add_bullet(doc, " High variance between stylists; the same individual is categorized differently by different barbers.", "Inconsistency:")
    add_bullet(doc, " Clients cannot visualize the final result on their own face before cutting occurs.", "Zero Pre-Cut Visualization:")
    add_bullet(doc, " Haircuts take four to twelve months to grow back, causing prolonged emotional distress.", "Irreversibility:")
    add_bullet(doc, " Existing mobile apps use flat 2D cartoon stickers that look ridiculous and fail to blend with skin or lighting.", "Crude 2D Sticker Overlays:")
    add_bullet(doc, " Consultations fail to account for whether the client's hair is naturally curly, wavy, or straight.", "Ignoring Hair Texture:")
    add_bullet(doc, " Consultation details are forgotten immediately; no digital records are kept for future visits.", "Absence of Data History:")

    # 5.4 Limitations
    add_h2(doc, "5.4 Limitations of Conventional Styling Approaches")
    add_p(doc, "Conventional styling approaches are severely limited by human memory and cognitive biases. In busy salons, barbers default to two or three standard cuts they are fastest at performing, regardless of client suitability. Furthermore, physical lookbooks quickly become outdated, unhygienic, and provide zero interactive personalization.", space_before=4, space_after=10, line_spacing=1.5)

    # 5.5 Proposed System
    add_h2(doc, "5.5 Proposed System Architecture & Philosophy")
    add_p(doc, "The proposed StyleAI platform replaces subjective guesswork with an automated, science-backed computational pipeline. StyleAI combines Google MediaPipe Face Mesh, geometric ratio analysis, deep neural network classification, Google Gemini generative reasoning, and identity-preserving virtual try-on inpainting into an intuitive web interface.", space_before=4, space_after=10, line_spacing=1.5)

    # 5.6 Advantages
    add_h2(doc, "5.6 Key Advantages of the Proposed StyleAI System")
    add_p(doc, "StyleAI delivers substantial operational and aesthetic benefits over existing methods:", space_before=4, space_after=6, line_spacing=1.5)
    add_bullet(doc, " 468 landmark vertices guarantee consistent, reproducible face shape classification within milliseconds.", "1. Objective Biometric Precision:")
    add_bullet(doc, " Google Gemini AI clearly explains WHY a haircut harmonizes with facial proportions and WHICH cuts to avoid.", "2. Explainable AI Rationales:")
    add_bullet(doc, " The virtual try-on module preserves personal facial identity, skin tone, and eyes while showing realistic haircuts.", "3. Identity-Preserving Try-On:")
    add_bullet(doc, " Cuts are filtered by whether hair is straight, wavy, curly, or coily, ensuring practical daily styling.", "4. Texture & Maintenance Awareness:")
    add_bullet(doc, " Secure MongoDB database preserves all past scans, recommendations, and try-ons.", "5. Complete Consultation History:")
    add_bullet(doc, " Operates in any browser on desktop, tablet, or mobile without app store downloads.", "6. Universal Web Accessibility:")

    # 5.7 Input Analysis
    add_h2(doc, "5.7 Input Analysis & Validation Criteria")
    add_p(doc, "The system accepts two distinct input channels:", space_before=4, space_after=6, line_spacing=1.5)
    add_bullet(doc, " Full Name (String, 2–50 chars), Email (RFC 5322 format), Password (bcrypt hashed, min 6 chars), Gender (Male/Female/Other), Hair Texture (Straight/Wavy/Curly/Coily).", "Form Input Data:")
    add_bullet(doc, " JPEG, PNG, or WEBP image format, maximum file size 10 MB, minimum resolution 480x480 pixels, maximum resolution 4096x4096 pixels. Must contain exactly one clearly visible human face.", "Visual Portrait Input:")

    # 5.8 Output Analysis
    add_h2(doc, "5.8 Output Analysis & Delivery Pipeline")
    add_p(doc, "The system delivers a structured, multi-component output payload to the client interface:", space_before=4, space_after=6, line_spacing=1.5)
    add_bullet(doc, " Classified face shape (e.g., 'Oval') accompanied by a confidence percentage (e.g., 96.4%) and probability scores across all 7 classes.", "1. Morphological Classification:")
    add_bullet(doc, " Visual breakdown of face length, forehead width, cheekbone width, jaw width, and mandibular curvature.", "2. Anthropometric Measurements:")
    add_bullet(doc, " Ranked haircut cards with style photos, maintenance ratings, and required styling products.", "3. Hairstyle Catalog Recommendations:")
    add_bullet(doc, " Natural-language paragraphs synthesized by Gemini AI explaining the styling rationale, contraindicated haircuts, and grooming tips.", "4. Generative AI Styling Dossier:")
    add_bullet(doc, " Photorealistic before-and-after composite previews of selected hairstyles.", "5. Virtual Try-On Visualizations:")

    # 5.9 Module Analysis (14 modules)
    add_h2(doc, "5.9 Comprehensive Module-by-Module Functional Analysis")
    add_p(doc, "StyleAI is architected around fourteen decoupled, single-responsibility software modules:", space_before=4, space_after=6, line_spacing=1.5)
    add_bullet(doc, " Ingests user credentials, validates uniqueness, applies bcrypt salt hashing, and creates user documents in MongoDB.", "Module 1: User Registration:")
    add_bullet(doc, " Verifies user credentials, validates bcrypt passwords, and issues cryptographic HMAC-SHA256 JWT bearer tokens.", "Module 2: Login Authentication:")
    add_bullet(doc, " Central personalized user portal showing quick scan actions, recent analyses, favorite haircuts, and stats.", "Module 3: Dashboard:")
    add_bullet(doc, " Manages file drag-and-drop, validates MIME types, verifies file size bounds, and streams WebRTC camera frames.", "Module 4: Image Upload & Camera Streaming:")
    add_bullet(doc, " Decodes binary buffers, converts color spaces (BGR to RGB), applies histogram equalization, and resizes matrices.", "Module 5: OpenCV Processing:")
    add_bullet(doc, " Utilizes BlazeFace convolutional detector to locate human face bounding boxes and verify facial presence.", "Module 6: Face Detection:")
    add_bullet(doc, " Tracks 468 three-dimensional coordinate vertices across the forehead, temples, cheekbones, jaw, and chin.", "Module 7: MediaPipe Face Mesh:")
    add_bullet(doc, " Maps specific vertex IDs to anatomical landmarks and extracts scale-invariant Euclidean distances and angles.", "Module 8: Facial Landmark Detection:")
    add_bullet(doc, " Feeds 9-dimensional geometric feature vectors into the trained TensorFlow MLP model to predict face shape.", "Module 9: Face Shape Classification:")
    add_bullet(doc, " Constructs tailored prompt payloads and queries Google Gemini 2.0 Flash to synthesize structured styling advice.", "Module 10: Gemini AI Recommendation:")
    add_bullet(doc, " Persists scan logs, classified shapes, confidence scores, and advice payloads into MongoDB with query APIs.", "Module 11: Recommendation History:")
    add_bullet(doc, " Allows users to inspect account details, update gender and hair texture preferences, and reset passwords.", "Module 12: Profile Management:")
    add_bullet(doc, " Displays academic documentation, project objectives, Atmiya University details, and developer credits.", "Module 13: About Module:")
    add_bullet(doc, " Provides user support channels, feedback submission forms, and salon partnership inquiry interfaces.", "Module 14: Contact Module:")

    # 5.10 SWOT Analysis
    add_h2(doc, "5.10 SWOT Analysis")
    add_p(doc, "A comprehensive SWOT analysis evaluates the internal strengths and weaknesses of StyleAI alongside external opportunities and threats:", space_before=4, space_after=6, line_spacing=1.5)

    swot_headers = ["Category", "Key Strategic Factors", "Architectural Response / Strategy"]
    swot_rows = [
        ["STRENGTHS (S)", "Sub-46ms facial inference; 94.6% accuracy; Gemini AI rationales; 468 3D landmarks; zero licensing cost.", "Capitalize on high accuracy and explainable AI to build consumer trust and salon credibility."],
        ["WEAKNESSES (W)", "Requires front-facing photos; sensitive to severe underexposure; diffusion try-on requires GPU resources.", "Incorporate client-side lighting validation and provide lightweight local try-on fallback."],
        ["OPPORTUNITIES (O)", "Growing digital salon market; beauty e-commerce integration; virtual smart mirrors in salons; AR apps.", "Partner with cosmetology academies and integrate haircare product affiliate links."],
        ["THREATS (T)", "Potential Google Gemini API quota changes; competition from large tech firms (Apple/Google native AR).", "Design pluggable LLM architecture supporting local open-source LLMs (Llama, Mistral) if needed."]
    ]
    add_table_data(doc, swot_headers, swot_rows, col_widths=[1.5, 2.7, 2.6],
                   caption="Table 5.1: SWOT Analysis Matrix for StyleAI Recommendation System")

    # 5.11 Feasibility Analysis
    add_h2(doc, "5.11 In-Depth Feasibility Analysis")
    add_p(doc, "The detailed feasibility study confirms that StyleAI is viable across all dimensions:", space_before=4, space_after=6, line_spacing=1.5)

    feas_headers = ["Feasibility Dimension", "Evaluation Criteria", "Feasibility Outcome & Verification"]
    feas_rows = [
        ["Technical Feasibility", "Hardware capabilities, ML inference speeds, browser APIs", "VERIFIED: Sub-46ms latency on standard CPUs, full WebRTC support."],
        ["Operational Feasibility", "User adoption ease, salon workflow integration", "VERIFIED: Intuitive 3-click workflow requires zero technical user training."],
        ["Economic Feasibility", "Development costs, operational licensing expenses", "VERIFIED: 100% open-source stack, free educational API tiers, zero cost."],
        ["Schedule Feasibility", "16-week delivery milestone compliance", "VERIFIED: All 8 Agile sprints completed on schedule with full QA pass."]
    ]
    add_table_data(doc, feas_headers, feas_rows, col_widths=[1.6, 2.3, 2.9],
                   caption="Table 5.2: Technical, Operational, and Economic Feasibility Matrix")

    # 5.12 Chapter Summary
    add_h2(doc, "5.12 Chapter Summary")
    add_p(doc, "Chapter 5 presented an exhaustive System Analysis. It examined the conventional salon consultation process and exposed its subjectivity, inconsistency, and lack of historical continuity. It outlined the advantages of the proposed StyleAI system, analyzed input and output data flows, provided a detailed functional analysis of all fourteen core modules, conducted a strategic SWOT analysis, and reaffirmed complete feasibility. Chapter 6 transitions to the concrete System Design and architectural models.", space_before=4, space_after=12, line_spacing=1.5)
    doc.add_page_break()

def build_chapter_6(doc):
    add_h1(doc, "CHAPTER – 6\nSYSTEM DESIGN")
    add_p(doc, "", space_after=6)

    # 6.1 Introduction
    add_h2(doc, "6.1 Introduction")
    add_p(doc, "System Design translates the requirements and functional models established in previous chapters into concrete architectural blueprints, data structures, subsystem interfaces, and deployment topologies. Software design serves as the crucial bridge between abstract problem definitions and tangible source code implementation.", space_before=4, space_after=6, line_spacing=1.5)
    add_p(doc, "This chapter documents the 3-tier layered system architecture, formalizes UML design diagrams (Use Case, Activity, Sequence, Class, Deployment), presents Data Flow Diagrams (DFD Level 0 and Level 1), details the Entity-Relationship (ER) model and MongoDB database schemas, and outlines system workflows and security architectures.", space_before=4, space_after=10, line_spacing=1.5)

    # 6.2 System Architecture
    add_h2(doc, "6.2 System Architecture")
    add_p(doc, "StyleAI is architected upon a clean, decoupled 3-tier layered architecture consisting of the Presentation Tier, Application Tier, and Data Storage Tier:", space_before=4, space_after=6, line_spacing=1.5)
    add_bullet(doc, " Implemented using modern HTML5, Vanilla CSS3 Glassmorphism, Bootstrap 5, and JavaScript (ES6+). Interacts directly with client camera hardware via WebRTC, manages DOM updates, renders charts, and stores JWT session tokens.", "1. Presentation Tier (Client Layer):")
    add_bullet(doc, " Powered by Python Flask 3.x WSGI microframework. Orchestrates REST API routing, PyJWT authentication middleware, OpenCV matrix image processing, Google MediaPipe 468-point mesh extraction, TensorFlow DNN classification, Google Gemini generative prompting, and virtual try-on pipelines.", "2. Application Tier (Server & AI Layer):")
    add_bullet(doc, " Powered by MongoDB 7.x NoSQL document engine. Stores user credentials, hairstyle catalog records, facial analysis metrics, and virtual try-on snapshots with high-speed indexing.", "3. Data & Storage Tier (Persistence Layer):")

    add_figure(doc, "arch_diagram.png", "Figure 6.1: 3-Tier Layered System Architecture of StyleAI", width=3.0)

    # 6.3 Use Case Diagram
    add_h2(doc, "6.3 UML Use Case Diagram")
    add_p(doc, "The UML Use Case Diagram specifies the operational interactions between system actors (Guest User, Registered User, Salon Stylist, System Administrator) and core platform capabilities:", space_before=4, space_after=6, line_spacing=1.5)

    add_figure(doc, "use_case_diagram.png", "Figure 6.2: UML Use Case Diagram: Actors and System Functions", width=3.0)

    # 6.4 Activity Diagram
    add_h2(doc, "6.4 UML Activity Diagram")
    add_p(doc, "The UML Activity Diagram models the dynamic operational control flow of the facial scanning, morphological classification, and recommendation lifecycle:", space_before=4, space_after=6, line_spacing=1.5)

    add_figure(doc, "activity_diagram.png", "Figure 6.3: UML Activity Diagram: Scan and Recommendation Flow", width=3.0)

    # 6.5 Sequence Diagram
    add_h2(doc, "6.5 UML Sequence Diagram")
    add_p(doc, "The UML Sequence Diagram traces the exact chronological order of HTTP requests, internal method calls, and external API invocations during the face analysis pipeline:", space_before=4, space_after=6, line_spacing=1.5)

    add_figure(doc, "sequence_diagram.png", "Figure 6.4: UML Sequence Diagram: End-to-End API Interaction Traces", width=3.0)

    # 6.6 Class Diagram
    add_h2(doc, "6.6 UML Class Diagram")
    add_p(doc, "The UML Class Diagram illustrates the object-oriented design, model entities, service classes, attributes, methods, and relationships within StyleAI:", space_before=4, space_after=6, line_spacing=1.5)

    add_figure(doc, "class_diagram.png", "Figure 6.5: UML Class Diagram: Core Models & Business Services", width=3.0)

    # 6.7 DFD Level 0
    add_h2(doc, "6.7 Data Flow Diagram: Level 0 (Context Level DFD)")
    add_p(doc, "The Level 0 Context DFD depicts the high-level boundary of the StyleAI core engine, showing data flows between external entities (User, Google Gemini API, MongoDB):", space_before=4, space_after=6, line_spacing=1.5)

    add_figure(doc, "dfd_level0.png", "Figure 6.6: Data Flow Diagram Level 0: Context Level DFD", width=3.0)

    # 6.8 DFD Level 1
    add_h2(doc, "6.8 Data Flow Diagram: Level 1 (Subsystem Deconstruction)")
    add_p(doc, "The Level 1 DFD decomposes the system into five sub-processes (Auth, Mesh Extraction, DNN Classification, Recommendation Filtering, GenAI Try-On) and three data stores (D1 Users, D2 Hairstyles, D3 Analyses):", space_before=4, space_after=6, line_spacing=1.5)

    add_figure(doc, "dfd_level1.png", "Figure 6.7: Data Flow Diagram Level 1: Subsystem Deconstruction", width=3.0)

    # 6.9 ER Diagram
    add_h2(doc, "6.9 Entity-Relationship (ER) Diagram")
    add_p(doc, "The Entity-Relationship Diagram defines the MongoDB NoSQL document collections, primary keys, foreign reference keys, and relational cardinalities across USERS, ANALYSES, HAIRSTYLES, and TRYONS:", space_before=4, space_after=6, line_spacing=1.5)

    add_figure(doc, "er_diagram.png", "Figure 6.8: Entity-Relationship & NoSQL Document Schema Diagram", width=3.0)

    # 6.10 Database Design
    add_h2(doc, "6.10 Database Design & Schema Specifications")
    add_p(doc, "StyleAI utilizes MongoDB 7.x, a document-oriented NoSQL database. Four core collections are formally defined in Table 6.1:", space_before=4, space_after=6, line_spacing=1.5)

    db_headers = ["Collection Name", "Key Document Attributes", "Data Types", "Indexing & Constraints"]
    db_rows = [
        ["users", "_id, name, email, password_hash, gender, role, preferences, created_at", "ObjectId, String, String, String, String, String, Dict, Date", "Unique index on email; role defaults to 'user'"],
        ["hairstyles", "_id, name, slug, face_shapes, gender, hair_types, length, maintenance, popularity", "ObjectId, String, String, Array[Str], String, Array[Str], String, String, Int", "Compound index on (gender, length); unique slug"],
        ["analyses", "_id, user_id, image_path, face_shape, confidence, all_scores, ai_advice, created_at", "ObjectId, ObjectId, String, String, Float, Dict, Dict, Date", "Foreign Key reference to users._id; indexed created_at"],
        ["tryons", "_id, user_id, analysis_id, hairstyle_id, result_image_url, provider, created_at", "ObjectId, ObjectId, ObjectId, ObjectId, String, String, Date", "FK references to users, analyses, hairstyles"]
    ]
    add_table_data(doc, db_headers, db_rows, col_widths=[1.2, 2.4, 1.6, 1.6],
                   caption="Table 6.1: MongoDB Collection Schemas & Data Attribute Descriptions")

    # 6.11 Navigation Flow
    add_h2(doc, "6.11 System Navigation Flow")
    add_p(doc, "The web interface provides an intuitive navigation hierarchy: Landing Page (index.html) -> Authentication (login.html / register.html) -> Main Dashboard (dashboard.html) -> Portrait Analysis & Camera Scan (analyze.html) -> Recommendation & Try-On Results (results.html) -> Historical Archives (history.html) -> User Settings (profile.html) -> Admin Console (admin.html).", space_before=4, space_after=10, line_spacing=1.5)

    # 6.12 Workflow
    add_h2(doc, "6.12 End-to-End Operational Workflow")
    add_p(doc, "The operational workflow proceeds sequentially: 1. User arrives on the portal and authenticates. 2. User captures or uploads a facial portrait. 3. Flask receives the payload and invokes OpenCV. 4. MediaPipe extracts 468 landmarks. 5. Feature extractor calculates 9 ratios. 6. Keras DNN classifies face shape. 7. Hairstyle catalog is filtered. 8. Gemini AI synthesizes custom rationales. 9. Results render dynamically in the browser. 10. Scan is persisted to database.", space_before=4, space_after=10, line_spacing=1.5)

    # 6.13 Deployment Diagram
    add_h2(doc, "6.13 UML Deployment Diagram")
    add_p(doc, "The UML Deployment Diagram illustrates the physical and network distribution of hardware devices, software execution containers, database clusters, and cloud AI services:", space_before=4, space_after=6, line_spacing=1.5)

    add_figure(doc, "deployment_diagram.png", "Figure 6.9: UML Deployment Diagram: Distributed Hardware & Cloud Nodes", width=3.0)

    # 6.14 Security Design
    add_h2(doc, "6.14 Security Architecture & Cryptographic Design")
    add_p(doc, "StyleAI implements robust, multi-layer security protections:", space_before=4, space_after=6, line_spacing=1.5)
    add_bullet(doc, " Passwords are never stored in plain text. Salting and hashing are performed using bcrypt with 12 algorithmic work rounds.", "Password Cryptography:")
    add_bullet(doc, " Stateless session tokens signed with HMAC-SHA256, containing expiration claims (24 hours) and role authorizations.", "JWT Bearer Authentication:")
    add_bullet(doc, " Restricts API requests to authorized origins, preventing Cross-Site Request Forgery (CSRF).", "Cross-Origin Resource Sharing (CORS):")
    add_bullet(doc, " Uploaded files are stripped of execution permissions, assigned cryptographically secure UUID filenames, and stored outside the public web root.", "Secure File Upload Handling:")
    add_bullet(doc, " All API endpoints enforce strict schema validation to block injection attacks.", "Input Sanitization:")

    # 6.15 Chapter Summary
    add_h2(doc, "6.15 Chapter Summary")
    add_p(doc, "Chapter 6 established the comprehensive architectural and structural design of StyleAI. It detailed the 3-tier architecture, documented UML Use Case, Activity, Sequence, Class, and Deployment diagrams, illustrated DFD Level 0 and Level 1 flows, and modeled the MongoDB ER schema and database design. Navigation hierarchies and security protocols were thoroughly defined. With design blueprints in place, Chapter 7 transitions to the concrete System Implementation.", space_before=4, space_after=12, line_spacing=1.5)
    doc.add_page_break()

print("Enhanced Chapter 4, 5, and 6 builder ready.")
