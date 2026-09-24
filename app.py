import streamlit as st

from config import APP_TITLE, MODEL
from storage import (
    get_or_create_participant,
    save_result,
    load_results,
)
from ai_service import (
    generate_task,
    evaluate_solution,
)
from charts import (
    render_summary,
    render_competency_chart,
    render_competency_radar,
    render_difficulty_heatmap,
    render_task_chart,
)
from ui import (
    inject_css,
    language_to_code,
    difficulty_label,
    competency_label,
)
from research import render_research_dashboard


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
    st.session_state.participant_id = (
        get_or_create_participant()
    )

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
        [
            "Python",
            "JavaScript",
            "C++",
            "HTML/CSS",
            "SQL",
        ],
    )

    difficulty = st.selectbox(
        "Բարդություն / Difficulty",
        [
            "Easy / Հեշտ",
            "Medium / Միջին",
            "Hard / Բարդ",
        ],
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
        f"Մասնակցի կեղծանուն / Pseudonym: "
        f"**{participant_id}**"
    )

    st.caption(
        f"Model: {MODEL}"
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
        " Նոր փորձ",
        " Արդյունք",
        " Հետազոտություն",
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

        st.write(
            f"**{language}** · "
            f"**{difficulty}** · "
            f"**{competency}**"
        )

        # ----------------------------------------------------
        # GENERATE AI TASK
        # ----------------------------------------------------

        if st.button(
            "Գեներացնել AI առաջադրանք / Generate AI Task",
            use_container_width=True,
            type="primary",
        ):

            with st.spinner(
                "Luna-ն պատրաստում է առաջադրանքը..."
            ):

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

        # ====================================================
        # GENERATED TASK
        # ====================================================

        if st.session_state.task:

            task = st.session_state.task

            st.divider()

            # ------------------------------------------------
            # TASK TITLE
            # ------------------------------------------------

            # st.markdown(
            #     f"## {task.get('title', 'AI Task')}"
            # )

            # ------------------------------------------------
            # TASK DESCRIPTION
            # ------------------------------------------------

            st.info(
                task.get(
                    "description",
                    "Առաջադրանքի նկարագրությունը հասանելի չէ։",
                )
            )

            # ------------------------------------------------
            # AI GENERATED CODE
            # ------------------------------------------------

            st.markdown(
                "###  AI-generated code"
            )

            st.code(
                task.get("code", ""),
                language=language_to_code(language),
            )

            # ------------------------------------------------
            # REQUIREMENTS
            # ------------------------------------------------

            requirements = task.get(
                "requirements",
                [],
            )

            if requirements:

                st.markdown(
                    "### 📋 Պահանջներ / Requirements"
                )

                for requirement in requirements:

                    st.write(
                        "• " + str(requirement)
                    )

            # =================================================
            # DETERMINE TASK TYPE
            # =================================================

            is_easy = difficulty.startswith(
                "Easy"
            )

            is_understanding = competency.startswith(
                "Կոդի ընկալում"
            )

            is_error_detection = competency.startswith(
                "Սխալի հայտնաբերում և ուղղում"
            )

            is_adaptation = competency.startswith(
                "Կոդի ադապտացում"
            )

            is_optimization = competency.startswith(
                "Կոդի օպտիմալացում"
            )

            # =================================================
            # DEFAULT ANSWERS
            # =================================================

            selected_option = None
            explanation = ""
            student_code = ""

            # =================================================
            # 1. CODE UNDERSTANDING + EASY
            # =================================================

            if is_understanding and is_easy:

                st.markdown(
                    "### 🔍 Կոդի ընկալում — Թեստ"
                )

                st.caption(
                    "Կարդա AI-ի գեներացրած կոդը և ընտրիր "
                    "ճիշտ պատասխանը։"
                )

                options = task.get(
                    "quiz_options",
                    [],
                )

                if len(options) == 4:

                    selected_option = st.radio(
                        "Ի՞նչ է անում այս կոդը?",
                        options,
                        key="understanding_quiz",
                    )

                else:

                    st.error(
                        "AI-ն չի վերադարձրել ճիշտ 4 "
                        "ընտրանք։ Առաջադրանքը չի կարող "
                        "ցուցադրվել որպես թեստ։"
                    )

            # =================================================
            # 2. CODE UNDERSTANDING + MEDIUM / HARD
            # =================================================

            elif is_understanding:

                st.markdown(
                    "### 🔍 Կոդի ընկալում / Code Understanding"
                )

                st.caption(
                    "Այս բաժնում գնահատվում է միայն "
                    "կոդի բացատրությունը։"
                )

                explanation = st.text_area(
                    "Բացատրիր՝ ինչ է անում կոդը / "
                    "Explain what the code does",
                    height=150,
                    placeholder=(
                        "Գրիր քո վերլուծությունը..."
                    ),
                    key="understanding_explanation",
                )

            # =================================================
            # 3. ERROR DETECTION + EASY
            # =================================================

            elif is_error_detection and is_easy:

                st.markdown(
                    "### 1️⃣ Կոդի ընկալում — Թեստ"
                )

                st.caption(
                    "Կարդա կոդը և ընտրիր ճիշտ պատասխանը։ "
                    "Այս մասում ստուգվում է միայն "
                    "կոդի ընկալումը։"
                )

                options = task.get(
                    "quiz_options",
                    [],
                )

                if len(options) == 4:

                    selected_option = st.radio(
                        "Ի՞նչ է անում այս կոդը?",
                        options,
                        key="error_easy_quiz",
                    )

                else:

                    st.error(
                        "AI-ն չի վերադարձրել ճիշտ 4 "
                        "ընտրանք։ Առաջադրանքը չի կարող "
                        "ցուցադրվել որպես թեստ։"
                    )

                st.divider()

                st.markdown(
                    "### 2️⃣ Կոդի ուղղում"
                )

                st.caption(
                    "Գտիր կոդի սխալը և ներկայացրու "
                    "ուղղված տարբերակը։"
                )

                student_code = st.text_area(
                    "💻 Ներկայացրու ուղղված կոդը",
                    height=220,
                    placeholder=(
                        "Գրիր այստեղ ուղղված կոդը..."
                    ),
                    key="easy_error_correction",
                )

            # =================================================
            # 4. CODE ADAPTATION + EASY
            # =================================================

            elif is_adaptation and is_easy:

                st.markdown(
                    "### 1️⃣ Կոդի ընկալում — Թեստ"
                )

                st.caption(
                    "Կարդա AI-ի գեներացրած կոդը և "
                    "ընտրիր ճիշտ պատասխանը։"
                )

                options = task.get(
                    "quiz_options",
                    [],
                )

                if len(options) == 4:

                    selected_option = st.radio(
                        "Ի՞նչ է անում այս կոդը?",
                        options,
                        key="adaptation_easy_quiz",
                    )

                else:

                    st.error(
                        "AI-ն չի վերադարձրել ճիշտ 4 "
                        "ընտրանք։ Առաջադրանքը չի կարող "
                        "ցուցադրվել որպես թեստ։"
                    )

                st.divider()

                st.markdown(
                    "### 2️⃣ Կոդի ադապտացում"
                )

                st.caption(
                    "Հարմարեցրու կոդը ներկայացված "
                    "նոր պահանջին։"
                )

                student_code = st.text_area(
                    "💻 Ներկայացրու ադապտացված կոդը",
                    height=220,
                    placeholder=(
                        "Գրիր այստեղ փոփոխված կոդը..."
                    ),
                    key="easy_adaptation",
                )

            # =================================================
            # 5. CODE OPTIMIZATION + EASY
            # =================================================

            elif is_optimization and is_easy:

                st.markdown(
                    "### 1️⃣ Կոդի ընկալում — Թեստ"
                )

                st.caption(
                    "Կարդա AI-ի գեներացրած կոդը և "
                    "ընտրիր ճիշտ պատասխանը։"
                )

                options = task.get(
                    "quiz_options",
                    [],
                )

                if len(options) == 4:

                    selected_option = st.radio(
                        "Ի՞նչ է անում այս կոդը?",
                        options,
                        key="optimization_easy_quiz",
                    )

                else:

                    st.error(
                        "AI-ն չի վերադարձրել ճիշտ 4 "
                        "ընտրանք։ Առաջադրանքը չի կարող "
                        "ցուցադրվել որպես թեստ։"
                    )

                st.divider()

                st.markdown(
                    "### 2️⃣ Կոդի օպտիմալացում"
                )

                st.caption(
                    "Բարելավիր կոդի արդյունավետությունը "
                    "կամ կառուցվածքը՝ պահպանելով "
                    "դրա ճիշտ աշխատանքը։"
                )

                student_code = st.text_area(
                    "💻 Ներկայացրու օպտիմալացված կոդը",
                    height=220,
                    placeholder=(
                        "Գրիր այստեղ օպտիմալացված կոդը..."
                    ),
                    key="easy_optimization",
                )

            # =================================================
            # 6. OTHER COMPETENCIES
            # =================================================

            else:

                st.markdown(
                    f"### 🛠️ {competency}"
                )

                explanation = st.text_area(
                    "Բացատրիր՝ ինչ է անում կոդը "
                    "կամ որտեղ է խնդիրը",
                    height=150,
                    placeholder=(
                        "Գրիր քո վերլուծությունը..."
                    ),
                    key="explanation",
                )

                student_code = st.text_area(
                    "💻 Ներկայացրու քո փոփոխած/ուղղված կոդը",
                    height=220,
                    placeholder=(
                        "Գրիր լուծումը այստեղ..."
                    ),
                    key="student_code",
                )

            # =================================================
            # SUBMIT
            # =================================================

            st.divider()

            if st.button(
                "Հանձնել և գնահատել / Submit & Evaluate",
                use_container_width=True,
                type="primary",
            ):

                # ------------------------------------------------
                # VALIDATION — UNDERSTANDING + EASY
                # ------------------------------------------------

                if is_understanding and is_easy:

                    if not selected_option:

                        st.warning(
                            "Ընտրիր պատասխան։"
                        )

                        st.stop()

                # ------------------------------------------------
                # VALIDATION — ERROR DETECTION + EASY
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
                # VALIDATION — ADAPTATION + EASY
                # ------------------------------------------------

                elif is_adaptation and is_easy:

                    if not selected_option:

                        st.warning(
                            "Ընտրիր թեստի պատասխանը։"
                        )

                        st.stop()

                    if not student_code.strip():

                        st.warning(
                            "Ներկայացրու ադապտացված կոդը։"
                        )

                        st.stop()

                # ------------------------------------------------
                # VALIDATION — OPTIMIZATION + EASY
                # ------------------------------------------------

                elif is_optimization and is_easy:

                    if not selected_option:

                        st.warning(
                            "Ընտրիր թեստի պատասխանը։"
                        )

                        st.stop()

                    if not student_code.strip():

                        st.warning(
                            "Ներկայացրու օպտիմալացված կոդը։"
                        )

                        st.stop()

                # ------------------------------------------------
                # VALIDATION — OTHER COMPETENCIES
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
                        # VALIDATE EVALUATION
                        # -----------------------------------------

                        if not isinstance(
                            evaluation,
                            dict,
                        ):

                            raise ValueError(
                                "AI գնահատման արդյունքը պետք է "
                                "լինի dictionary։"
                            )

                        # -----------------------------------------
                        # SAVE EVALUATION IN SESSION
                        # -----------------------------------------

                        st.session_state.evaluation = (
                            evaluation
                        )

                        st.session_state.submitted = True

                        # -----------------------------------------
                        # CREATE COMPLETE RESEARCH RESULT
                        # -----------------------------------------

                        result = {

                            # =====================================
                            # EXPERIMENT METADATA
                            # =====================================

                            "participant_id": (
                                participant_id
                            ),

                            "task_id": task.get(
                                "task_id",
                                "UNKNOWN",
                            ),

                            "language": language,

                            "difficulty": difficulty,

                            "competency": competency,

                            # =====================================
                            # COMPLETE TASK
                            # =====================================

                            "task": {
                                "task_id": task.get(
                                    "task_id",
                                    "UNKNOWN",
                                ),

                                # "title": "Առաջադրանք",

                                "description": task.get(
                                    "description",
                                    "",
                                ),

                                "code": task.get(
                                    "code",
                                    "",
                                ),

                                "requirements": task.get(
                                    "requirements",
                                    [],
                                ),

                                "quiz_options": task.get(
                                    "quiz_options",
                                    [],
                                ),

                                "correct_option_index": task.get(
                                    "correct_option_index",
                                    None,
                                ),
                            },

                            # =====================================
                            # COMPLETE STUDENT SOLUTION
                            # =====================================

                            "student_solution": {

                                "selected_option": (
                                    selected_option
                                    if selected_option
                                    is not None
                                    else ""
                                ),

                                "explanation": (
                                    explanation
                                ),

                                "submitted_code": (
                                    student_code
                                ),
                            },

                            # =====================================
                            # AI EVALUATION
                            # =====================================

                            "evaluation": evaluation,

                            # =====================================
                            # FUTURE EXPERT EVALUATION
                            # =====================================

                            "expert_evaluation": {},
                        }

                        # -----------------------------------------
                        # SAVE RESULT
                        # -----------------------------------------

                        save_result(
                            result
                        )

                        st.session_state.last_result = (
                            result
                        )

                        # -----------------------------------------
                        # SUCCESS
                        # -----------------------------------------

                        st.success(
                            "Գնահատումն ավարտված է։"
                        )

                        st.info(
                            "Արդյունքը տեսնելու համար ընտրիր "
                            "վերևի 📊 Արդյունք բաժինը։"
                        )

                    except Exception as exc:

                        st.error(
                            f"Գնահատման սխալ՝ {exc}"
                        )

    # --------------------------------------------------------
    # Current experiment
    # --------------------------------------------------------

    with col2:

        with st.container(
            key="settings-panel"
        ):

            st.markdown(
                """
                <div class="settings-header">
                    <div class="settings-header-title">
                        Ընթացիկ փորձի կարգավորումներ
                    </div>
                    <div class="settings-header-subtitle">
                        Current experiment settings
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            st.metric(
                "Լեզու / Language",
                language,
            )

            st.metric(
                "Մակարդակ / Difficulty",
                difficulty_label(
                    difficulty
                ),
            )

            st.metric(
                "Տիպ / Competency",
                competency_label(
                    competency
                ),
            )


# ============================================================
# TAB 2 — RESULTS
# ============================================================

with tab2:

    st.markdown(
        '<div id="result-section"></div>',
        unsafe_allow_html=True,
    )

    evaluation = (
        st.session_state.evaluation
    )

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
            0,
        )

        understanding = evaluation.get(
            "understanding",
            0,
        )

        problem_detection = evaluation.get(
            "problem_detection",
            0,
        )

        adaptation = evaluation.get(
            "adaptation",
            0,
        )

        optimization = evaluation.get(
            "optimization",
            0,
        )

        # ----------------------------------------------------
        # Metrics
        # ----------------------------------------------------

        c1, c2, c3, c4, c5 = (
            st.columns(5)
        )

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

        except (
            TypeError,
            ValueError,
        ):

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
                    "—",
                )
            )

        with right:

            st.markdown(
                "### 🎯 Զարգացման ուղղություն / Improvement"
            )

            st.warning(
                evaluation.get(
                    "improvement",
                    "—",
                )
            )

        st.markdown(
            "### 🤖 AI Feedback"
        )

        st.write(
            evaluation.get(
                "feedback",
                "—",
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

        if not isinstance(
            all_results,
            list,
        ):

            all_results = []

        participant_results = [
            r
            for r in all_results
            if isinstance(r, dict)
            and r.get(
                "participant_id"
            ) == participant_id
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

    all_results = load_results()

    if not isinstance(
        all_results,
        list,
    ):

        all_results = []

    render_research_dashboard(
        all_results
    )