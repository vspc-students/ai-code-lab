
import streamlit as st

from config import APP_TITLE, MODEL
from storage import get_or_create_participant, save_result, load_results
from ai_service import generate_task, evaluate_solution
from charts import (
    render_summary,
    render_competency_chart,
    render_competency_radar,
    render_difficulty_heatmap,
    render_task_chart,
)
from ui import inject_css, language_to_code, difficulty_label, competency_label


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title=APP_TITLE,
    page_icon="💻",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_css()


# ============================================================
# SESSION STATE
# ============================================================

if "task" not in st.session_state:
    st.session_state.task = None

if "evaluation" not in st.session_state:
    st.session_state.evaluation = None

if "submitted" not in st.session_state:
    st.session_state.submitted = False

if "participant_id" not in st.session_state:
    st.session_state.participant_id = get_or_create_participant()

if "last_result" not in st.session_state:
    st.session_state.last_result = None


participant_id = st.session_state.participant_id


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown("## 💻 AI Code Lab")

    st.caption(
        "AI-ի գեներացրած կոդի հասկացման, "
        "ուղղման և ադապտացման փորձարարական հարթակ"
    )

    st.divider()

    language = st.selectbox(
        "Ծրագրավորման լեզու",
        ["Python", "JavaScript", "C++", "HTML/CSS", "SQL"],
    )

    difficulty = st.selectbox(
        "Բարդություն / Difficulty",
        ["Easy / Հեշտ", "Medium / Միջին", "Hard / Բարդ"],
    )

    competency = st.selectbox(
        "Կոմպետենտություն / Competency",
        [
            "Կոդի ընկալում / Code Understanding",
            "Սխալի հայտնաբերում և ուղղում / Error Detection & Correction",
            "Կոդի ադապտացում / Code Adaptation",
            "Կոդի օպտիմալացում / Code Optimization",
        ],
    )

    st.divider()

    st.info(
        f"Մասնակցի կեղծանուն / Pseudonym: **{participant_id}**"
    )

    st.caption(f"Model: {MODEL}")

    st.caption(
        "Հետազոտական տվյալները պահվում են JSON ձևաչափով։"
    )


# ============================================================
# HEADER
# ============================================================

st.markdown(
    """
    <div class="hero">
        <div class="hero-title">💻 AI Code Lab</div>
        <div class="hero-subtitle">
            Ուսանողների ծրագրավորման կոմպետենտության գնահատում՝
            AI-ի գեներացրած կոդի հետ աշխատանքի միջոցով
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# TABS
# ============================================================

tab1, tab2, tab3 = st.tabs(
    [
        "🧪 Նոր փորձ",
        "📊 Արդյունք",
        "ℹ️ Հետազոտություն",
    ]
)


# ============================================================
# TAB 1 — NEW EXPERIMENT
# ============================================================

with tab1:

    col1, col2 = st.columns([2, 1])

    # --------------------------------------------------------
    # Experiment settings
    # --------------------------------------------------------

    with col1:

        st.markdown("### 🧪 Փորձի կարգավորում")

        st.write(
            f"**{language}** · "
            f"**{difficulty}** · "
            f"**{competency}**"
        )

        if st.button(
            "✨ Գեներացնել AI առաջադրանք / Generate AI Task",
            use_container_width=True,
            type="primary",
        ):

            with st.spinner("Luna-ն պատրաստում է առաջադրանքը..."):

                try:

                    task = generate_task(
                        language,
                        difficulty,
                        competency,
                    )

                    st.session_state.task = task
                    st.session_state.evaluation = None
                    st.session_state.submitted = False
                    st.session_state.last_result = None

                    st.rerun()

                except Exception as exc:

                    st.error(
                        f"Առաջադրանքի ստեղծման սխալ՝ {exc}"
                    )

    # --------------------------------------------------------
    # Current experiment
    # --------------------------------------------------------

    with col2:

        st.markdown("### 📌 Ընթացիկ փորձ")

        st.metric(
            "Լեզու / Language",
            language,
        )

        st.metric(
            "Մակարդակ / Difficulty",
            difficulty_label(difficulty),
        )

        st.metric(
            "Տիպ / Competency",
            competency_label(competency),
        )


    # ========================================================
    # GENERATED TASK
    # ========================================================

    if st.session_state.task:

        task = st.session_state.task

        st.divider()

        st.markdown(
            f"## 🧩 {task.get('title', 'AI Task')}"
        )

        st.info(
            task.get(
                "description",
                "Առաջադրանքի նկարագրությունը հասանելի չէ։"
            )
        )

        # ----------------------------------------------------
        # AI generated code
        # ----------------------------------------------------

        st.markdown("### 🤖 AI-generated code")

        st.code(
            task.get("code", ""),
            language=language_to_code(language),
        )

        # ----------------------------------------------------
        # Requirements
        # ----------------------------------------------------

        requirements = task.get("requirements", [])

        if requirements:

            st.markdown(
                "### 📋 Պահանջներ / Requirements"
            )

            for requirement in requirements:
                st.write("• " + str(requirement))

        st.divider()


        # ====================================================
        # DETERMINE TASK TYPE
        # ====================================================

        is_easy = difficulty.startswith("Easy")

        is_understanding = competency.startswith(
            "Կոդի ընկալում"
        )

        is_error_detection = competency.startswith(
            "Սխալի հայտնաբերում և ուղղում"
        )


        # ====================================================
        # DEFAULT ANSWERS
        # ====================================================

        selected_option = None
        explanation = ""
        student_code = ""


        # ====================================================
        # 1. CODE UNDERSTANDING + EASY
        # ====================================================

        if is_understanding and is_easy:

            st.markdown(
                "### 🔍 Կոդի ընկալում / Code Understanding"
            )

            st.caption(
                "Ընտրիր ճիշտ տարբերակը։"
            )

            options = task.get(
                "quiz_options",
                []
            )

            if len(options) == 4:

                selected_option = st.radio(
                    "Ի՞նչ է անում այս կոդը / What does this code do?",
                    options,
                    key="understanding_quiz",
                )

            else:

                st.error(
                    "Quiz-ի համար անհրաժեշտ է 4 ընտրանք։"
                )


        # ====================================================
        # 2. CODE UNDERSTANDING + MEDIUM/HARD
        # ====================================================

        elif is_understanding:

            st.markdown(
                "### 🔍 Կոդի ընկալում / Code Understanding"
            )

            st.caption(
                "Այս բաժնում գնահատվում է միայն կոդի բացատրությունը։"
            )

            explanation = st.text_area(
                "Բացատրիր՝ ինչ է անում կոդը / Explain what the code does",
                height=150,
                placeholder="Գրիր քո վերլուծությունը...",
                key="understanding_explanation",
            )


        # ====================================================
        # 3. ERROR DETECTION + EASY
        # ====================================================

        elif is_error_detection and is_easy:

            st.markdown(
                "### 1️⃣ Կոդի ընկալում — Թեստ"
            )

            st.caption(
                "Կարդա կոդը և ընտրիր ճիշտ պատասխանը։ "
                "Այս մասում ստուգվում է միայն կոդի ընկալումը։"
            )

            options = task.get(
                "quiz_options",
                []
            )

            if len(options) == 4:

                selected_option = st.radio(
                    "Ի՞նչ է անում այս կոդը?",
                    options,
                    key="error_easy_quiz",
                )

            else:

                st.error(
                    "AI-ն չի վերադարձրել ճիշտ 4 ընտրանք։ "
                    "Առաջադրանքը չի կարող ցուցադրվել որպես թեստ։"
                )

            # ------------------------------------------------
            # Code correction
            # ------------------------------------------------

            st.divider()

            st.markdown(
                "### 2️⃣ Կոդի ուղղում"
            )

            st.caption(
                "Գտիր կոդի սխալը և ներկայացրու ուղղված տարբերակը։"
            )

            student_code = st.text_area(
                "💻 Ներկայացրու ուղղված կոդը",
                height=220,
                placeholder="Գրիր այստեղ ուղղված կոդը...",
                key="easy_error_correction",
            )


        # ====================================================
        # 4. OTHER COMPETENCIES
        # ====================================================

        else:

            st.markdown(
                f"### 🛠️ {competency}"
            )

            explanation = st.text_area(
                "Բացատրիր՝ ինչ է անում կոդը կամ որտեղ է խնդիրը",
                height=150,
                placeholder="Գրիր քո վերլուծությունը...",
                key="explanation",
            )

            student_code = st.text_area(
                "💻 Ներկայացրու քո փոփոխած/ուղղված կոդը",
                height=220,
                placeholder="Գրիր լուծումը այստեղ...",
                key="student_code",
            )


        # ====================================================
        # SUBMIT
        # ====================================================

        st.divider()

        if st.button(
            "Հանձնել և գնահատել / Submit & Evaluate",
            use_container_width=True,
            type="primary",
        ):

            # ------------------------------------------------
            # Validation — Understanding + Easy
            # ------------------------------------------------

            if is_understanding and is_easy:

                if not selected_option:

                    st.warning(
                        "Ընտրիր պատասխան։"
                    )

                    st.stop()


            # ------------------------------------------------
            # Validation — Error Detection + Easy
            # ------------------------------------------------

            elif is_error_detection and is_easy:

                if not selected_option:

                    st.warning(
                        "Ընտրիր թեստի պատասխանը։"
                    )

                    st.stop()

                if not student_code.strip():

                    st.warning(
                        "Ներկայացրու ուղղված կոդը։"
                    )

                    st.stop()


            # ------------------------------------------------
            # Validation — Other competencies
            # ------------------------------------------------

            else:

                if not explanation.strip():

                    st.warning(
                        "Գրիր քո բացատրությունը։"
                    )

                    st.stop()

                if not student_code.strip():

                    st.warning(
                        "Ներկայացրու կոդը։"
                    )

                    st.stop()


            # =================================================
            # EVALUATION
            # =================================================

            with st.spinner(
                "Luna-ն վերլուծում է քո աշխատանքը..."
            ):

                try:

                    evaluation = evaluate_solution(
                        task=task,
                        explanation=explanation,
                        student_code=student_code,
                        selected_option=selected_option,
                        language=language,
                        difficulty=difficulty,
                        competency=competency,
                    )

                    # -----------------------------------------
                    # Validate evaluation
                    # -----------------------------------------

                    if not isinstance(evaluation, dict):

                        raise ValueError(
                            "AI գնահատման արդյունքը պետք է լինի dictionary։"
                        )


                    # -----------------------------------------
                    # Save evaluation
                    # -----------------------------------------

                    st.session_state.evaluation = evaluation
                    st.session_state.submitted = True


                    # -----------------------------------------
                    # Create research result
                    # -----------------------------------------

                    result = {
                        "participant_id": participant_id,
                        "task_id": task.get(
                            "task_id",
                            "UNKNOWN"
                        ),
                        "language": language,
                        "difficulty": difficulty,
                        "competency": competency,
                        "task_title": task.get(
                            "title",
                            "AI Task"
                        ),
                        "evaluation": evaluation,
                    }


                    # -----------------------------------------
                    # Save result
                    # -----------------------------------------

                    save_result(result)

                    st.session_state.last_result = result


                    st.success(
                        "Գնահատումն ավարտված է։"
                    )

                    st.info(
                        "Արդյունքը տեսնելու համար ընտրիր վերևի "
                        "📊 Արդյունք բաժինը։"
                    )


                except Exception as exc:

                    st.error(
                        f"Գնահատման սխալ՝ {exc}"
                    )


# ============================================================
# TAB 2 — RESULTS
# ============================================================

with tab2:

    st.markdown(
        '<div id="result-section"></div>',
        unsafe_allow_html=True,
    )

    evaluation = st.session_state.evaluation


    # ========================================================
    # NO RESULT
    # ========================================================

    if not evaluation:

        st.info(
            "Արդյունքը կհայտնվի այն բանից հետո, "
            "երբ ուսանողը կհանձնի առաջադրանքը։"
        )


    # ========================================================
    # RESULT
    # ========================================================

    else:

        st.markdown(
            "## 📊 Competency Dashboard"
        )


        # ----------------------------------------------------
        # Scores
        # ----------------------------------------------------

        total = evaluation.get(
            "total",
            0
        )

        understanding = evaluation.get(
            "understanding",
            0
        )

        problem_detection = evaluation.get(
            "problem_detection",
            0
        )

        adaptation = evaluation.get(
            "adaptation",
            0
        )

        optimization = evaluation.get(
            "optimization",
            0
        )


        # ----------------------------------------------------
        # Metrics
        # ----------------------------------------------------

        c1, c2, c3, c4, c5 = st.columns(5)

        c1.metric(
            "Ընդհանուր / Total",
            f"{total}/100",
        )

        c2.metric(
            "Ընկալում / Understanding",
            f"{understanding}%",
        )

        c3.metric(
            "Սխալի հայտնաբերում / Detection",
            f"{problem_detection}%",
        )

        c4.metric(
            "Ադապտացում / Adaptation",
            f"{adaptation}%",
        )

        c5.metric(
            "Օպտիմալացում / Optimization",
            f"{optimization}%",
        )


        st.divider()


        # ----------------------------------------------------
        # Main score
        # ----------------------------------------------------

        try:

            score = float(total)

        except (TypeError, ValueError):

            score = 0

        score = min(
            max(score, 0),
            100,
        )

        st.progress(
            score / 100
        )

        st.markdown(
            f'<div class="score">{score:.0f}/100</div>',
            unsafe_allow_html=True,
        )

        st.caption(
            "AI Code Lab · Competency Score"
        )


        # ----------------------------------------------------
        # Feedback
        # ----------------------------------------------------

        left, right = st.columns(2)


        with left:

            st.markdown(
                "### 💪 Ուժեղ կողմ / Strength"
            )

            st.success(
                evaluation.get(
                    "strength",
                    "—"
                )
            )


        with right:

            st.markdown(
                "### 🎯 Զարգացման ուղղություն / Improvement"
            )

            st.warning(
                evaluation.get(
                    "improvement",
                    "—"
                )
            )


        st.markdown(
            "### 🤖 AI Feedback"
        )

        st.write(
            evaluation.get(
                "feedback",
                "—"
            )
        )


        st.divider()


        # ====================================================
        # RESEARCH PROFILE
        # ====================================================

        st.markdown(
            "### 🔬 Հետազոտական պրոֆիլ"
        )

        st.caption(
            "Գրաֆիկները կառուցվում են տվյալ մասնակցի "
            "կուտակված արդյունքների հիման վրա։"
        )


        # ----------------------------------------------------
        # Load participant results
        # ----------------------------------------------------

        all_results = load_results()

        if not isinstance(all_results, list):

            all_results = []


        participant_results = [
            r
            for r in all_results
            if isinstance(r, dict)
            and r.get("participant_id") == participant_id
        ]


        # ----------------------------------------------------
        # Summary
        # ----------------------------------------------------

        render_summary(
            participant_results
        )


        st.divider()


        # ----------------------------------------------------
        # Competency profile
        # ----------------------------------------------------

        render_competency_chart(
            participant_results
        )


        st.divider()


        # ----------------------------------------------------
        # Radar
        # ----------------------------------------------------

        render_competency_radar(
            participant_results
        )


        st.divider()


        # ----------------------------------------------------
        # Difficulty × Competency
        # ----------------------------------------------------

        render_difficulty_heatmap(
            participant_results
        )


        st.divider()


        # ----------------------------------------------------
        # Progress
        # ----------------------------------------------------

        render_task_chart(
            participant_results
        )


# ============================================================
# TAB 3 — RESEARCH
# ============================================================

with tab3:

    st.markdown(
        "## ℹ️ Հետազոտության մասին"
    )

    st.markdown(
        """
### Ինչ է ուսումնասիրում AI Code Lab-ը

Նախագիծը ուսումնասիրում է, թե որքան արդյունավետ են ուսանողները
կարողանում աշխատել արհեստական բանականության կողմից գեներացված
ծրագրային կոդի հետ։

Ուսումնասիրվում են չորս հիմնական կարողություններ.

- 🔍 Կոդի ընկալում / Code Understanding
- 🐞 Սխալի հայտնաբերում և ուղղում / Error Detection & Correction
- 🔄 Կոդի ադապտացում / Code Adaptation
- ⚡ Կոդի օպտիմալացում / Code Optimization

### 🔬 Առաջարկվող գիտական նորույթ

AI Code Lab-ը չի չափում միայն «կոդ գրելու» կարողությունը։
Փորձը կառուցվում է AI-գեներացված կոդի **կառուցվածքային միջամտությունների**
վրա՝ ընկալում → սխալի հայտնաբերում/ուղղում → ադապտացում → օպտիմալացում։

Յուրաքանչյուր առաջադրանքի համար պահպանվում են նույնականացվող,
բայց անձնական տվյալներ չպարունակող հետազոտական դաշտեր՝ մասնակից,
լեզու, բարդություն, կոմպետենտություն, առաջադրանքի ID և 0–100
գնահատականներ։ Սա հնարավորություն է տալիս հետագայում ուսումնասիրել
կոմպետենտության պրոֆիլները և տարբեր պայմանների ազդեցությունը։

### 🧪 Գիտափորձի որակի բարելավումներ

- նույն կառուցվածքով առաջադրանքների բազմակի գեներացում,
- difficulty × competency × language գործոնների վերահսկվող համադրություն,
- AI-ի գնահատման միասնական rubric,
- առաջադրանքի և գնահատման տվյալների JSON provenance,
- յուրաքանչյուր մասնակցի կեղծանուն՝ առանց անվան/էլ․ փոստի,
- հետագա վիճակագրական վերլուծության համար պատրաստ տվյալների կառուցվածք։

**Կարևոր մեթոդաբանական քայլ.** ցուցահանդեսի վերջնական հետազոտության
մեջ AI գնահատականները ցանկալի է համեմատել նաև դասախոսի/փորձագետի
գնահատականի հետ՝ inter-rater agreement և AI-ի գնահատման
հուսալիությունը ուսումնասիրելու համար։
"""
    )


    st.divider()


    # ========================================================
    # DATA STRUCTURE
    # ========================================================

    st.markdown(
        "### 🗂️ Տվյալների պահպանման կառուցվածք"
    )

    st.code(
        """{
  "participant_id": "P-7F3A91",
  "task_id": "TASK-...",
  "language": "Python",
  "difficulty": "Easy / Հեշտ",
  "competency": "Կոդի ընկալում / Code Understanding",
  "evaluation": {
    "understanding": 90,
    "problem_detection": 0,
    "adaptation": 0,
    "optimization": 0,
    "total": 90
  }
}""",
        language="json",
    )


    st.caption(
        "AI Code Lab · Research Prototype"
    )

