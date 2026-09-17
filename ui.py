# ui.py
import streamlit as st


def inject_css():
    st.markdown(
        """
<style>


:root {
    --acl-primary: #2F80ED;
    --acl-primary-hover: #1D6FD6;
    --acl-surface: #F5FBFF;
    --acl-border: rgba(128,128,128,.25);
    --acl-radius: 18px;
    --acl-hero-radius: 22px;
    --acl-button-radius: 12px;
    --acl-content-max-width: 1400px;
    --acl-sidebar-width: 330px;
    --acl-title-size: 42px;
}

/* General */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}

.block-container {
    max-width: var(--acl-content-max-width);
    padding-top: 2rem;
}

/* Hero */
.hero {
    padding: 30px;
    border-radius: var(--acl-hero-radius);
    border: 1px solid rgba(128,128,128,.2);
    margin-bottom: 25px;
    background-color: var(--acl-surface);
}

.hero-title {
    font-size: var(--acl-title-size);
    font-weight: 800;
    margin-bottom: 50px;
}

.hero-subtitle {
    font-size: 18px;
    opacity: .7;
}

/* Cards / results */
.card {
    padding: 22px;
    border-radius: var(--acl-radius);
    border: 1px solid var(--acl-border);
    margin-bottom: 15px;
}

.score {
    font-size: 48px;
    font-weight: 800;
}

.small-label {
    font-size: 13px;
    opacity: .6;
}

.badge {
    padding: 6px 12px;
    border-radius: 20px;
    border: 1px solid rgba(128,128,128,.3);
    display: inline-block;
}

textarea {
    font-family: monospace !important;
}

/* Buttons — փոխիր այստեղ */
.stButton > button {
    border-radius: var(--acl-button-radius);
    font-weight: 650;
    transition: all .15s ease;
}

.stButton > button:hover {
    transform: translateY(-1px);
}

/* Primary button — եթե Streamlit-ի DOM-ը փոխվի, այս հատվածը
   կարելի է վերաձևավորել։ */
button[kind="primary"] {
    border-radius: var(--acl-button-radius);
}

/* Sidebar */
[data-testid="stSidebar"] {
    border-right: 1px solid var(--acl-border);
}

/* Right information column */
[data-testid="column"]:has(.metric-container) {
    min-height: 100px;
}

/* Code blocks */
[data-testid="stCode"] {
    border-radius: 14px;
}

/* Mobile */
@media (max-width: 900px) {
    .hero-title {
        font-size: 30px;
        margin-bottom: 25px;
    }
    .hero {
        padding: 22px;
    }
}

</style>
""",
        unsafe_allow_html=True,
    )


def language_to_code(language):
    return {
        "Python": "python",
        "JavaScript": "javascript",
        "C++": "cpp",
        "HTML/CSS": "html",
        "SQL": "sql",
    }.get(language, "text")


def difficulty_label(value):
    return value.split(" / ")[1] if " / " in value else value


def competency_label(value):
    return value.split(" / ")[0]
