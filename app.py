
import sqlite3
import csv
from io import BytesIO, StringIO
from datetime import datetime
from pathlib import Path

import fitz
import plotly.express as px
import streamlit as st


# --------------------------------------------------
# 1. APPLICATION CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Career Compass",
    page_icon="🧭",
    layout="wide"
)

DB_NAME = Path(__file__).resolve().parent / "career_compass.db"
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB


# --------------------------------------------------
# 2. CAREER SKILL DATABASE
# --------------------------------------------------

CAREERS = {
    "Python Developer": {
        "Python", "SQL", "Git", "Django", "Flask",
        "REST API", "OOP", "Data Structures"
    },
    "Web Developer": {
        "HTML", "CSS", "JavaScript", "React",
        "Python", "SQL", "Git", "REST API"
    },
    "Data Analyst": {
        "Python", "SQL", "Excel", "Power BI",
        "Statistics", "Pandas", "Data Visualization"
    },
    "AI/ML Beginner": {
        "Python", "Statistics", "NumPy", "Pandas",
        "Machine Learning", "SQL", "Data Visualization"
    }
}


# --------------------------------------------------
# 3. LEARNING RECOMMENDATIONS
# --------------------------------------------------

LEARNING = {
    "Python": "Learn variables, conditions, loops, functions and OOP.",
    "SQL": "Practice SELECT, WHERE, JOIN, GROUP BY and subqueries.",
    "Git": "Learn repositories, commits, branches and GitHub.",
    "Django": "Build a web application using Django.",
    "Flask": "Create a small web application or REST API.",
    "REST API": "Learn HTTP methods, JSON and API requests.",
    "OOP": "Practice classes, objects, inheritance and polymorphism.",
    "Data Structures": "Practice lists, stacks, queues, trees and searching.",
    "HTML": "Build accessible web pages using semantic HTML.",
    "CSS": "Practice Flexbox, Grid and responsive layouts.",
    "JavaScript": "Learn DOM manipulation, events and asynchronous code.",
    "React": "Build reusable components and interactive interfaces.",
    "Excel": "Practice formulas, pivot tables and charts.",
    "Power BI": "Create dashboards from sample datasets.",
    "Statistics": "Study averages, probability and distributions.",
    "Pandas": "Practice cleaning and analyzing tabular data.",
    "NumPy": "Learn arrays and numerical operations.",
    "Machine Learning": "Start with regression and classification.",
    "Data Visualization": "Create charts and explain patterns in data."
}


# --------------------------------------------------
# 4. DATABASE FUNCTIONS
# --------------------------------------------------

def initialize_database():
    """Create the analysis table if it does not exist."""
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS analyses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                filename TEXT NOT NULL,
                career TEXT NOT NULL,
                matched TEXT NOT NULL,
                missing TEXT NOT NULL,
                score REAL NOT NULL
            )
        """)


def save_analysis(filename, career, matched, missing, score):
    """Save one analysis in SQLite."""
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("""
            INSERT INTO analyses (
                created_at, filename, career,
                matched, missing, score
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            filename,
            career,
            ", ".join(matched),
            ", ".join(missing),
            score
        ))


def load_history():
    """Return the latest 100 saved analyses."""
    with sqlite3.connect(DB_NAME) as conn:
        return conn.execute("""
            SELECT id, created_at, filename, career,
                   matched, missing, score
            FROM analyses
            ORDER BY id DESC
            LIMIT 100
        """).fetchall()


# --------------------------------------------------
# 5. PDF RESUME EXTRACTION
# --------------------------------------------------

def extract_pdf_text(pdf_bytes):
    """Extract selectable text from a PDF file."""
    text_pages = []

    with fitz.open(
        stream=BytesIO(pdf_bytes),
        filetype="pdf"
    ) as document:

        if document.is_encrypted:
            raise ValueError(
                "Password-protected PDFs are not supported."
            )

        if len(document) == 0:
            raise ValueError("The PDF has no pages.")

        for page in document:
            text_pages.append(page.get_text())

    return "\n".join(text_pages)


# --------------------------------------------------
# 6. SKILL MATCHING ENGINE
# --------------------------------------------------

def analyze_resume(text, career):
    """
    Compare resume keywords with the selected career.
    This is keyword matching, not a trained AI model.
    """
    text_lower = text.lower()
    required_skills = CAREERS[career]

    matched = sorted(
        skill for skill in required_skills
        if skill.lower() in text_lower
    )

    missing = sorted(
        required_skills - set(matched)
    )

    score = round(
        len(matched) / len(required_skills) * 100,
        2
    )

    return matched, missing, score


# --------------------------------------------------
# 7. CSV EXPORT
# --------------------------------------------------

def history_to_csv(history):
    """Convert analysis history into a downloadable CSV."""
    output = StringIO()
    writer = csv.writer(output)

    writer.writerow([
        "ID", "Date", "Filename", "Career",
        "Matched Skills", "Missing Skills", "Score"
    ])

    for row in history:
        writer.writerow(row)

    return output.getvalue().encode("utf-8-sig")


# --------------------------------------------------
# 8. INITIALIZE APPLICATION
# --------------------------------------------------

initialize_database()

if "report" not in st.session_state:
    st.session_state["report"] = None


# --------------------------------------------------
# 9. SIDEBAR
# --------------------------------------------------

with st.sidebar:
    st.title("🧭 Career Compass")
    st.caption("Your career planning assistant")

    page = st.radio(
        "Navigation",
        ["Resume Analyzer", "Analysis History", "About Project"]
    )

    st.divider()

    st.subheader("Choose target career")

    career = st.selectbox(
        "Career",
        list(CAREERS.keys()),
        key="selected_career"
    )

    st.info(
        "Privacy: analysis runs locally. "
        "The database saves filenames and skill results, "
        "not the full resume text."
    )


# --------------------------------------------------
# 10. RESUME ANALYZER PAGE
# --------------------------------------------------

if page == "Resume Analyzer":

    st.title("🧭 AI-Powered Career Compass")

    st.write(
        "Analyze your resume, compare your skills with a "
        "target career, and discover topics to learn next."
    )

    st.caption(
        f"Selected career: **{career}**"
    )

    st.divider()

    uploaded_file = st.file_uploader(
        "Upload your resume in PDF format",
        type=["pdf"],
        help="Maximum file size: 5 MB. Use a text-based PDF."
    )

    if uploaded_file is not None:

        st.success(f"Selected file: {uploaded_file.name}")

        if uploaded_file.size > MAX_FILE_SIZE:

            st.error(
                "Your file exceeds 5 MB. "
                "Please upload a smaller PDF."
            )

        elif st.button(
            "Analyze My Resume",
            type="primary",
            use_container_width=True
        ):

            try:
                resume_text = extract_pdf_text(
                    uploaded_file.getvalue()
                )

                if not resume_text.strip():

                    st.warning(
                        "No selectable text was found. "
                        "The PDF may be scanned. OCR support "
                        "is not included in this version."
                    )

                else:
                    matched, missing, score = analyze_resume(
                        resume_text,
                        career
                    )

                    report = {
                        "filename": uploaded_file.name,
                        "career": career,
                        "matched": matched,
                        "missing": missing,
                        "score": score
                    }

                    save_analysis(
                        uploaded_file.name,
                        career,
                        matched,
                        missing,
                        score
                    )

                    st.session_state["report"] = report

            except (ValueError, RuntimeError):
                st.error(
                    "The PDF could not be processed. "
                    "Try a valid, non-password-protected PDF."
                )

            except Exception:
                st.error(
                    "An unexpected error occurred. "
                    "Please try another PDF."
                )

    # Display the latest report
    report = st.session_state.get("report")

    if report:

        st.divider()
        st.header("📊 Your Career Match Report")

        st.write(
            f"**Resume:** {report['filename']}  \n"
            f"**Target career:** {report['career']}"
        )

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Keyword Match",
            f"{report['score']:.2f}%"
        )

        col2.metric(
            "Skills Found",
            len(report["matched"])
        )

        col3.metric(
            "Skills Not Found",
            len(report["missing"])
        )

        st.progress(report["score"] / 100)

        st.caption(
            "This percentage measures keyword overlap only. "
            "It does not measure actual proficiency or predict "
            "your chances of getting hired."
        )

        left, right = st.columns(2)

        with left:
            st.subheader("✅ Matched Skills")

            if report["matched"]:
                for skill in report["matched"]:
                    st.write(f"✓ {skill}")
            else:
                st.write("No target keywords were found.")

        with right:
            st.subheader("📌 Potential Skill Gaps")

            if report["missing"]:
                for skill in report["missing"]:
                    st.write(f"• {skill}")
            else:
                st.write("All target keywords were found.")

        # Chart
        chart_data = {
            "Skill Category": ["Matched", "Not Found"],
            "Number of Skills": [
                len(report["matched"]),
                len(report["missing"])
            ]
        }

        figure = px.bar(
            chart_data,
            x="Skill Category",
            y="Number of Skills",
            title="Career Skill Coverage",
            text="Number of Skills"
        )

        figure.update_layout(
            yaxis_title="Number of skills",
            xaxis_title=""
        )

        st.plotly_chart(
            figure,
            use_container_width=True
        )

        # Learning recommendations
        st.subheader("🎯 Recommended Learning Plan")

        if report["missing"]:

            for number, skill in enumerate(
                report["missing"], start=1
            ):
                st.markdown(
                    f"**{number}. {skill}** — "
                    f"{LEARNING.get(skill, 'Practice this skill.')}"
                )

        else:
            st.success(
                "All listed career keywords were found. "
                "Next, build projects to demonstrate your skills."
            )

        # Downloadable report
        report_text = (
            "CAREER COMPASS - ANALYSIS REPORT\n"
            "================================\n"
            f"Resume: {report['filename']}\n"
            f"Target Career: {report['career']}\n"
            f"Keyword Match: {report['score']:.2f}%\n"
            f"Matched Skills: {', '.join(report['matched'])}\n"
            f"Potential Gaps: {', '.join(report['missing'])}\n\n"
            "Note: This score is based on keyword overlap only.\n"
        )

        st.download_button(
            "Download Text Report",
            data=report_text,
            file_name="career_compass_report.txt",
            mime="text/plain"
        )


# --------------------------------------------------
# 11. ANALYSIS HISTORY PAGE
# --------------------------------------------------

elif page == "Analysis History":

    st.title("📚 Analysis History")

    history = load_history()

    if not history:

        st.info(
            "No analyses saved yet. "
            "Upload a resume on the Resume Analyzer page."
        )

    else:

        st.write(
            f"Showing up to {len(history)} recent analyses."
        )

        display_data = [
            {
                "ID": row[0],
                "Date": row[1],
                "Filename": row[2],
                "Career": row[3],
                "Matched Skills": row[4],
                "Missing Skills": row[5],
                "Score": f"{row[6]:.2f}%"
            }
            for row in history
        ]

        st.dataframe(
            display_data,
            use_container_width=True,
            hide_index=True
        )

        st.download_button(
            "Export History as CSV",
            data=history_to_csv(history),
            file_name="career_compass_history.csv",
            mime="text/csv"
        )

        st.caption(
            "History is stored in your local SQLite database. "
            "This starter version does not include user accounts."
        )


# --------------------------------------------------
# 12. ABOUT PROJECT PAGE
# --------------------------------------------------

elif page == "About Project":

    st.title("ℹ️ About Career Compass")

    st.subheader("Problem Statement")

    st.write(
        "Students and job seekers may find it difficult to "
        "compare their listed skills with the requirements "
        "of a chosen career. This application provides a "
        "basic, explainable keyword comparison and learning guide."
    )

    st.subheader("Project Objectives")

    st.markdown("""
    - Extract selectable text from PDF resumes.
    - Compare resume keywords with predefined career skills.
    - Calculate a transparent keyword-match percentage.
    - Identify keywords that were not found.
    - Recommend learning topics.
    - Store analysis history in SQLite.
    """)

    st.subheader("Technology Stack")

    st.markdown("""
    - **Python:** application logic
    - **Streamlit:** web interface
    - **PyMuPDF:** PDF text extraction
    - **SQLite:** local database
    - **Plotly:** interactive charts
    """)

    st.subheader("Current Limitations")

    st.markdown("""
    - Uses keyword matching rather than a trained AI model.
    - May miss synonyms and variations in skill names.
    - Cannot confirm a person's actual skill level.
    - Scanned PDFs require OCR, which is not implemented.
    - Career recommendations are based on predefined rules.
    """)

    st.subheader("Future Enhancements")

    st.markdown("""
    - Semantic matching using NLP embeddings.
    - More career profiles and customizable skill requirements.
    - Login, registration and user-specific history.
    - OCR for scanned resumes.
    - Downloadable PDF reports.
    - Curated learning resources and project recommendations.
    """)


# --------------------------------------------------
# 13. FOOTER
# --------------------------------------------------

st.divider()

st.caption(
    "Career Compass | MCA Project | Python + Streamlit + SQLite"
)
