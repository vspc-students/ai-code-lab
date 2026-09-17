import os
import json
import re
import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv


load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError("OPENAI_API_KEY is not set")


st.set_page_config(
    page_title="AI Code Lab",
    page_icon="💻",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ------------------------------------------------------------
# OpenAI
# ------------------------------------------------------------



if api_key:
    client = OpenAI(api_key=api_key)
else:
    client = None


MODEL = "gpt-5.6-luna"


# ------------------------------------------------------------
# CSS
# ------------------------------------------------------------

st.markdown("""
<style>

#MainMenu {visibility: hidden;}
footer {visibility: hidden;}

.block-container {
    max-width: 1400px;
    padding-top: 2rem;
}

.hero {
    padding: 30px;
    border-radius: 22px;
    border: 1px solid rgba(128,128,128,.2);
    margin-bottom: 25px;
    background-color: #F5FBFF;
}

.hero-title {
    font-size: 42px;
    font-weight: 800;
    margin-bottom: 50px;
}

.hero-subtitle {
    font-size: 18px;
    opacity: .7;
}

.card {
    padding: 22px;
    border-radius: 18px;
    border: 1px solid rgba(128,128,128,.25);
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

</style>
""", unsafe_allow_html=True)


# ------------------------------------------------------------
# Session state
# ------------------------------------------------------------

if "task" not in st.session_state:
    st.session_state.task = None

if "evaluation" not in st.session_state:
    st.session_state.evaluation = None


# ------------------------------------------------------------
# Sidebar
# ------------------------------------------------------------

with st.sidebar:

    st.markdown("## 💻 AI Code Lab")

    st.caption(
        "AI-ի գեներացրած կոդի հասկացման, "
        "ուղղման և ադապտացման փորձարարական հարթակ"
    )

    st.divider()

    language = st.selectbox(
        "Ծրագրավորման լեզու",
        [
            "Python",
            "JavaScript",
            "C++",
            "HTML/CSS",
            "SQL"
        ]
    )

    difficulty = st.selectbox(
        "Բարդություն",
        [
            "Easy",
            "Medium",
            "Hard"
        ]
    )

    competency = st.selectbox(
        "Կոմպետենտություն",
        [
            "Կոդի ընկալում",
            "Սխալի հայտնաբերում և ուղղում",
            "Կոդի ադապտացում",
            "Կոդի օպտիմալացում"
        ]
    )

    st.divider()

    if client:
        st.success("OpenAI API՝ միացված")
    else:
        st.error("OPENAI_API_KEY-ը գտնված չէ")

    st.caption(f"Model: {MODEL}")


# ------------------------------------------------------------
# Header
# ------------------------------------------------------------

st.markdown("""
<div class="hero">

<div class="hero-title">
💻 AI Code Lab
</div>

<div class="hero-subtitle">
Ուսանողների ծրագրավորման կոմպետենտության
գնահատում՝ AI-ի գեներացրած կոդի հետ աշխատանքի միջոցով
</div>

</div>
""", unsafe_allow_html=True)


# ------------------------------------------------------------
# Generate task
# ------------------------------------------------------------

def generate_task(language, difficulty, competency):

    prompt = f"""
Ստեղծիր մեկ ծրագրավորման առաջադրանք ուսանողի համար։

Լեզու՝ {language}
Բարդություն՝ {difficulty}
Կոմպետենտություն՝ {competency}

Առաջադրանքը պետք է հիմնված լինի AI-ի գեներացրած կոդի վրա։

Պահանջներ.
- Տեքստերը հայերեն են։
- Կոդը տվյալ ծրագրավորման լեզվով է։
- Առաջադրանքը պետք է լինի իրատեսական։
- Մի տուր լուծումը։
- Կոդը պետք է ունենա լուծելի խնդիր։
-easy  մակարդակը լինի սկսնակ նոր սովորողների համար, medium  համեմատաբար հեշտ, բայց 1-2տարի սովորողների մակարդակի ուսանողների համար, hard  առաջադեմ ուսանողների համար։
-կոդի ավելացումները լինեն հնարավորինս կարճ, բայց հասկանալի։
-Պահանջը լինի կարճ, պարզ, բայց ամբողջական։
- Պատասխանը պետք է համապատասխանի տրամադրված JSON Schema-ին։
"""

    response = client.responses.create(
        model=MODEL,

        input=prompt,

        max_output_tokens=1500,

        text={
            "format": {
                "type": "json_schema",
                "name": "code_task",
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "title": {
                            "type": "string"
                        },
                        "description": {
                            "type": "string"
                        },
                        "code": {
                            "type": "string"
                        },
                        "requirements": {
                            "type": "array",
                            "items": {
                                "type": "string"
                            }
                        },
                        "expected_competency": {
                            "type": "string"
                        },
                        "test_hint": {
                            "type": "string"
                        }
                    },
                    "required": [
                        "title",
                        "description",
                        "code",
                        "requirements",
                        "expected_competency",
                        "test_hint"
                    ],
                    "additionalProperties": False
                }
            }
        }
    )

    try:
        return json.loads(response.output_text)
    except json.JSONDecodeError as e:
        st.error("OpenAI-ի վերադարձած JSON-ը ամբողջական չէ։")
        st.code(response.output_text)
        raise e


# ------------------------------------------------------------
# Evaluate student
# ------------------------------------------------------------

def evaluate_solution(task, explanation, student_code):

    prompt = f"""
Գնահատիր ուսանողի աշխատանքը։

ԱՌԱՋԱԴՐԱՆՔ
{json.dumps(task, ensure_ascii=False)}

ՈՒՍԱՆՈՂԻ ԲԱՑԱՏՐՈՒԹՅՈՒՆ
{explanation}

ՈՒՍԱՆՈՂԻ ԿՈԴ
{student_code}

Գնահատման չափանիշներ.

Կոդի ընկալում — 100 միավոր
Խնդրի հայտնաբերում — 100 միավոր
Լուծման/ադապտացման ճիշտություն — 100 միավոր
Բացատրության հստակություն — 100 միավոր

Գրիր կարճ հայերեն feedback։
"""

    response = client.responses.create(
        model=MODEL,
        input=prompt,
        max_output_tokens=800,

        text={
            "format": {
                "type": "json_schema",
                "name": "code_evaluation",
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "understanding": {
                            "type": "integer",
                            "minimum": 0,
                            "maximum": 100
                        },
                        "problem_detection": {
                            "type": "integer",
                            "minimum": 0,
                            "maximum": 100
                        },
                        "adaptation": {
                            "type": "integer",
                            "minimum": 0,
                            "maximum": 100
                        },
                        "clarity": {
                            "type": "integer",
                            "minimum": 0,
                            "maximum": 100
                        },
                        "total": {
                            "type": "integer",
                            "minimum": 0,
                            "maximum": 100
                        },
                        "feedback": {
                            "type": "string"
                        },
                        "strength": {
                            "type": "string"
                        },
                        "improvement": {
                            "type": "string"
                        }
                    },
                    "required": [
                        "understanding",
                        "problem_detection",
                        "adaptation",
                        "clarity",
                        "total",
                        "feedback",
                        "strength",
                        "improvement"
                    ],
                    "additionalProperties": False
                }
            }
        }
    )

    return json.loads(response.output_text)




# ============================================================
# MAIN
# ============================================================

tab1, tab2, tab3 = st.tabs([
    " Նոր փորձ",
    "📊 Արդյունք",
    "ℹ️ Հետազոտություն"
])


# ============================================================
# TAB 1
# ============================================================

with tab1:

    col1, col2 = st.columns([2, 1])

    with col1:

        st.markdown("### 🧪 Փորձի կարգավորում")

        st.write(
            f"**{language}** · "
            f"**{difficulty}** · "
            f"**{competency}**"
        )

        if st.button(
            "✨ Գեներացնել AI առաջադրանք",
            use_container_width=True,
            type="primary"
        ):

            if not client:
                st.error(
                    "Սկզբում սահմանեք OPENAI_API_KEY-ը։"
                )
            else:

                with st.spinner(
                    "Luna-ն պատրաստում է առաջադրանքը..."
                ):

                    try:

                        st.session_state.task = generate_task(
                            language,
                            difficulty,
                            competency
                        )

                        st.session_state.evaluation = None

                    except Exception as e:

                        st.error(
                            f"Առաջադրանքի ստեղծման սխալ՝ {e}"
                        )

    with col2:

        st.markdown("### 📌 Ընթացիկ փորձ")

        st.metric(
            "Լեզու",
            language
        )

        st.metric(
            "Մակարդակ",
            difficulty
        )

        st.metric(
            "Տիպ",
            competency
        )


    # --------------------------------------------------------
    # Task
    # --------------------------------------------------------

    if st.session_state.task:

        task = st.session_state.task

        st.divider()

        st.markdown(
            f"## 🧩 {task['title']}"
        )

        st.info(task["description"])

        st.markdown("### 🤖 AI-generated code")

        st.code(
            task["code"],
            language=(
                "javascript"
                if language == "JavaScript"
                else "cpp"
                if language == "C++"
                else "html"
                if language == "HTML/CSS"
                else "SQL"
                if language == "SQL"
                else "python"
            )
        )

        st.markdown("### 📋 Պահանջներ")

        for requirement in task["requirements"]:
            st.write("• " + requirement)

        st.divider()

        explanation = st.text_area(
            "🔍 Բացատրիր՝ ինչ է անում կոդը կամ որտեղ է խնդիրը",
            height=150,
            placeholder="Գրիր քո վերլուծությունը..."
        )

        student_code = st.text_area(
            "💻 Ներկայացրու քո փոփոխած/ուղղված կոդը",
            height=220,
            placeholder="Գրիր լուծումը այստեղ..."
        )

        if st.button(
            " Հանձնել և գնահատել",
            use_container_width=True,
            type="primary"
        ):

            if not explanation.strip():
                st.warning("Գրիր քո բացատրությունը։")

            elif not student_code.strip():
                st.warning("Ներկայացրու կոդը։")

            elif not client:
                st.error("OpenAI API-ն միացված չէ։")

            else:

                with st.spinner(
                    "Luna-ն վերլուծում է քո աշխատանքը..."
                ):

                    try:

                        st.session_state.evaluation = (
                            evaluate_solution(
                                task,
                                explanation,
                                student_code
                            )
                        )

                        st.success(
                            "Գնահատումն ավարտված է։"
                        )

                    except Exception as e:

                        st.error(
                            f"Գնահատման սխալ՝ {e}"
                        )


# ============================================================
# TAB 2
# ============================================================

with tab2:

    evaluation = st.session_state.evaluation

    if not evaluation:

        st.info(
            "Արդյունքը կհայտնվի այն բանից հետո, "
            "երբ ուսանողը կհանձնի առաջադրանքը։"
        )

    else:

        st.markdown("## 📊 Competency Dashboard")

        total = evaluation.get("total", 0)

        c1, c2, c3, c4, c5 = st.columns(5)

        c1.metric(
            "Ընդհանուր",
            f"{total}/100"
        )

        c2.metric(
            "Ընկալում",
            f"{evaluation.get('understanding', 0)}%"
        )

        c3.metric(
            "Սխալի հայտնաբերում",
            f"{evaluation.get('problem_detection', 0)}%"
        )

        c4.metric(
            "Ադապտացում",
            f"{evaluation.get('adaptation', 0)}%"
        )

        c5.metric(
            "Հստակություն",
            f"{evaluation.get('clarity', 0)}%"
        )

        st.divider()

        st.progress(
            min(max(total / 100, 0), 1)
        )

        st.markdown(
            f'<div class="score">{total}/100</div>',
            unsafe_allow_html=True
        )

        st.caption(
            "AI Code Adaptation / Competency Score"
        )

        st.divider()

        left, right = st.columns(2)

        with left:

            st.markdown("### 💪 Ուժեղ կողմ")

            st.success(
                evaluation.get(
                    "strength",
                    "—"
                )
            )

        with right:

            st.markdown(
                "### 🎯 Զարգացման ուղղություն"
            )

            st.warning(
                evaluation.get(
                    "improvement",
                    "—"
                )
            )

        st.markdown("### 🤖 AI Feedback")

        st.write(
            evaluation.get(
                "feedback",
                "—"
            )
        )


# ============================================================
# TAB 3
# ============================================================

with tab3:

    st.markdown("## ℹ️ Հետազոտության մասին")

    st.markdown("""
### Ինչ է ուսումնասիրում AI Code Lab-ը

Հավելվածի նպատակն է ուսումնասիրել, թե որքան արդյունավետ
են ուսանողները կարողանում աշխատել արհեստական բանականության
կողմից գեներացված ծրագրային կոդի հետ։

Ուսումնասիրվում են չորս հիմնական կարողություններ.

- 🔍 Կոդի ընկալում
- 🐞 Սխալների հայտնաբերում և ուղղում
- 🔄 Կոդի ադապտացում
- ⚡ Կոդի օպտիմալացում

Յուրաքանչյուր փորձի ընթացքում ուսանողը ստանում է AI-ի
գեներացրած կոդ, վերլուծում այն և ներկայացնում իր լուծումը։

AI-ն այնուհետև գնահատում է աշխատանքը նախապես սահմանված
չափանիշներով։
""")

    st.divider()

    st.markdown("### 🔬 Գիտական արժեք")

    st.write(
        "Հավելվածը կարող է օգտագործվել ուսանողների "
        "ծրագրավորման կոմպետենտության քանակական գնահատման "
        "և տարբեր բարդության մակարդակների համեմատական "
        "վերլուծության համար։"
    )

    st.divider()

    st.caption(
        "AI Code Lab · Research Prototype"
    )
