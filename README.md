# AI-Assisted IND Authoring from Scientific Papers

**An agentic LLM system that converts unstructured biomedical literature into structured, verified fields for generation of an IND filing introductory section**

### Goal 
Traditional LLM pipelines fail in regulated domains like pharma because they generate text without grounding in verifiable sources (i.e. hallucination).  In this project, I generate accurate outputs by combining 
structured extraction with cross-validation against established scientific databases.  

### Demo
You can try this project out at http://ind.nihaudit.com.  This demo starts with a preclinical KRAS paper (MRTX1133 by Mirati Therapuetics), performs structured extraction of fields (results shown in right pane), then displays 
the synthesized LLM IND introductory text in the bottom panel.  Importantly, you can click on each of the extracted fields to open up a modal with corresponding source evidence.

### System Overview 
