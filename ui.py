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

/* Cards */
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
/* =================================
   CURRENT EXPERIMENT SETTINGS
   ================================= */

.st-key-settings-panel {
    padding: 0 !important;

    background: #ffffff;

    border: 1px solid var(--acl-border);
    border-radius: var(--acl-radius);

    overflow: hidden;

    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.05);
}


/* Header */

.st-key-settings-panel .settings-header {
    padding: 20px 22px;

    background: var(--acl-surface);

    border-bottom: 1px solid var(--acl-border);
}

.st-key-settings-panel .settings-header-title {
    font-size: 20px;
    font-weight: 750;

    line-height: 1.3;

    color: #1f2937;
}

.st-key-settings-panel .settings-header-subtitle {
    margin-top: 5px;

    font-size: 13px;

    color: #6b7280;
}


/* Metrics area */

.st-key-settings-panel [data-testid="stMetric"] {
    margin: 2px 6px !important;
    padding: 3px 6px !important;

    background: #ffffff;

    border: 1px solid var(--acl-border);
    border-radius: 12px;

    box-shadow: none;
}

.st-key-settings-panel [data-testid="stMetricLabel"] {
    font-size: 13px !important;
    font-weight: 600 !important;

    color: #6b7280;
}

.st-key-settings-panel [data-testid="stMetricValue"] {
    font-size: 21px !important;
    font-weight: 700 !important;

    color: #1f2937;
}


/* Last metric */

.st-key-settings-panel [data-testid="stMetric"]:last-child {
    margin-bottom: 6px !important;
}
/* =========================
   BUTTONS
   ========================= */

div[data-testid="stButton"] > button {
    width: 100% !important;

    border-radius: var(--acl-button-radius) !important;

    font-weight: 650 !important;
    transition: all .15s ease !important;

    background-color: var(--acl-primary) !important;
    color: white !important;

    border: 1px solid var(--acl-primary) !important;
    box-shadow: none !important;
}

div[data-testid="stButton"] > button:hover {
    transform: translateY(-1px) !important;

    background-color: var(--acl-primary-hover) !important;
    color: white !important;

    border-color: var(--acl-primary-hover) !important;
}

div[data-testid="stButton"] > button:focus {
    background-color: var(--acl-primary) !important;
    color: white !important;

    border-color: var(--acl-primary) !important;
}

div[data-testid="stButton"] > button:active {
    background-color: var(--acl-primary-hover) !important;
    color: white !important;
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
