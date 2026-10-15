
# AI-Powered Career Compass

## Overview
A Python web application that analyzes PDF resumes,
compares listed skills against selected career profiles,
identifies potential skill gaps, and suggests learning topics.

## Features
- PDF resume text extraction
- Career-specific skill matching
- Skill gap report and match percentage
- Interactive chart
- SQLite analysis history
- Suggested learning topics

## Technology Stack
- Python
- Streamlit
- SQLite
- PyMuPDF
- Plotly

## Installation
1. Clone this repository.
2. Create and activate a Python virtual environment.
3. Install dependencies:

   pip install -r requirements.txt

4. Run the application:

   python -m streamlit run app.py

## Limitations
The current score uses keyword matching. It does not verify
skill proficiency, understand all synonyms, or predict hiring
outcomes. Scanned PDFs requiring OCR are not supported yet.

## Privacy
Resume text is processed locally by the application.
Analysis history stores filenames and extracted skill results.
Use synthetic resumes during testing and demonstrations.

## Future Scope
- Semantic skill matching
- User authentication
- More career profiles
- Exportable PDF reports
- OCR support for scanned resumes
