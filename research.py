# research.py

import numpy as np
import pandas as pd
import streamlit as st


# ============================================================
# SCORE COLUMNS
# ============================================================

SCORE_COLUMNS = [
    "understanding",
    "problem_detection",
    "adaptation",
    "optimization",
    "clarity",
    "total",
]


EXPERT_SCORE_COLUMNS = [
    "expert_understanding",
    "expert_problem_detection",
    "expert_adaptation",
    "expert_optimization",
    "expert_clarity",
    "expert_total",
]


# ============================================================
# HELPERS
# ============================================================

def _short_label(value):
    """
    Convert bilingual UI labels into their short form.

    Example:
        'Կոդի ընկալում / Code Understanding'
        ->
        'Կոդի ընկալում'
    """

    if not isinstance(value, str):
        return value

    return value.split(" / ")[0]


def _safe_text(value):
    """
    Convert a value to text suitable for CSV export.
    """

    if value is None:
        return ""

    if isinstance(value, (list, tuple)):
        return " | ".join(
            str(item)
            for item in value
        )

    if isinstance(value, dict):
        return str(value)

    return str(value)


def _get_nested_dict(
    data,
    key,
):
    """
    Safely retrieve a nested dictionary.
    """

    value = data.get(key, {})

    if isinstance(value, dict):
        return value

    return {}


# ============================================================
# DATA PREPARATION
# ============================================================

def build_research_dataframe(results):
    """
    Convert stored JSON research results into
    a flat pandas DataFrame.

    The resulting DataFrame contains:

    1. Experiment metadata
    2. Full task information
    3. Full student solution
    4. AI evaluation
    5. Optional future expert evaluation
    """

    rows = []

    for result in results:

        if not isinstance(result, dict):
            continue

        evaluation = _get_nested_dict(
            result,
            "evaluation",
        )

        task = _get_nested_dict(
            result,
            "task",
        )

        student_solution = _get_nested_dict(
            result,
            "student_solution",
        )

        expert_evaluation = _get_nested_dict(
            result,
            "expert_evaluation",
        )

        # ----------------------------------------------------
        # TASK FALLBACK
        # ----------------------------------------------------
        #
        # This supports both:
        #
        # New structure:
        #     result["task"]["title"]
        #
        # Old structure:
        #     result["task_title"]
        #
        task_title = (
            task.get(
                "title",
                result.get(
                    "task_title",
                    "",
                ),
            )
        )

        task_instructions = task.get(
            "instructions",
            result.get(
                "task_instructions",
                "",
            ),
        )

        task_code = task.get(
            "code",
            result.get(
                "task_code",
                "",
            ),
        )

        quiz_options = task.get(
            "quiz_options",
            result.get(
                "quiz_options",
                [],
            ),
        )

        correct_option_index = task.get(
            "correct_option_index",
            result.get(
                "correct_option_index",
            ),
        )

        # ----------------------------------------------------
        # STUDENT SOLUTION FALLBACK
        # ----------------------------------------------------

        student_selected_option = (
            student_solution.get(
                "selected_option",
                result.get(
                    "student_selected_option",
                    "",
                ),
            )
        )

        student_explanation = (
            student_solution.get(
                "explanation",
                result.get(
                    "student_explanation",
                    "",
                ),
            )
        )

        student_code = (
            student_solution.get(
                "submitted_code",
                result.get(
                    "student_code",
                    "",
                ),
            )
        )

        # ----------------------------------------------------
        # MAIN ROW
        # ----------------------------------------------------

        row = {

            # =================================================
            # EXPERIMENT METADATA
            # =================================================

            "participant_id": result.get(
                "participant_id"
            ),

            "task_id": result.get(
                "task_id"
            ),

            "timestamp": result.get(
                "timestamp"
            ),

            "language": result.get(
                "language"
            ),

            "difficulty": result.get(
                "difficulty"
            ),

            "competency": result.get(
                "competency"
            ),

            # =================================================
            # FULL TASK
            # =================================================

            "task_title": task_title,

            "task_instructions": (
                _safe_text(
                    task_instructions
                )
            ),

            "task_code": (
                _safe_text(
                    task_code
                )
            ),

            "quiz_options": (
                _safe_text(
                    quiz_options
                )
            ),

            "correct_option_index": (
                correct_option_index
            ),

            # =================================================
            # STUDENT SOLUTION
            # =================================================

            "student_selected_option": (
                _safe_text(
                    student_selected_option
                )
            ),

            "student_explanation": (
                _safe_text(
                    student_explanation
                )
            ),

            "student_code": (
                _safe_text(
                    student_code
                )
            ),

            # =================================================
            # AI EVALUATION
            # =================================================

            "understanding": evaluation.get(
                "understanding",
                np.nan,
            ),

            "problem_detection": evaluation.get(
                "problem_detection",
                np.nan,
            ),

            "adaptation": evaluation.get(
                "adaptation",
                np.nan,
            ),

            "optimization": evaluation.get(
                "optimization",
                np.nan,
            ),

            "clarity": evaluation.get(
                "clarity",
                np.nan,
            ),

            "total": evaluation.get(
                "total",
                np.nan,
            ),

            "ai_feedback": (
                _safe_text(
                    evaluation.get(
                        "feedback",
                        "",
                    )
                )
            ),

            "ai_strength": (
                _safe_text(
                    evaluation.get(
                        "strength",
                        "",
                    )
                )
            ),

            "ai_improvement": (
                _safe_text(
                    evaluation.get(
                        "improvement",
                        "",
                    )
                )
            ),

            # =================================================
            # FUTURE EXPERT EVALUATION
            # =================================================

            "expert_understanding": (
                expert_evaluation.get(
                    "understanding",
                    np.nan,
                )
            ),

            "expert_problem_detection": (
                expert_evaluation.get(
                    "problem_detection",
                    np.nan,
                )
            ),

            "expert_adaptation": (
                expert_evaluation.get(
                    "adaptation",
                    np.nan,
                )
            ),

            "expert_optimization": (
                expert_evaluation.get(
                    "optimization",
                    np.nan,
                )
            ),

            "expert_clarity": (
                expert_evaluation.get(
                    "clarity",
                    np.nan,
                )
            ),

            "expert_total": (
                expert_evaluation.get(
                    "total",
                    np.nan,
                )
            ),

            "expert_comments": (
                _safe_text(
                    expert_evaluation.get(
                        "comments",
                        "",
                    )
                )
            ),

            "expert_id": (
                expert_evaluation.get(
                    "expert_id",
                    "",
                )
            ),
        }

        rows.append(row)

    df = pd.DataFrame(rows)

    if df.empty:
        return df

    # ========================================================
    # NUMERIC CONVERSION
    # ========================================================

    numeric_columns = (
        SCORE_COLUMNS
        + EXPERT_SCORE_COLUMNS
    )

    for column in numeric_columns:

        if column in df.columns:

            df[column] = pd.to_numeric(
                df[column],
                errors="coerce",
            )

    # ========================================================
    # LABELS
    # ========================================================

    if "competency" in df.columns:

        df["competency_short"] = (
            df["competency"]
            .apply(_short_label)
        )

    if "difficulty" in df.columns:

        df["difficulty_short"] = (
            df["difficulty"]
            .apply(_short_label)
        )

    return df


# ============================================================
# STATISTICS
# ============================================================

def descriptive_statistics(
    df,
    score_column="total",
):
    """
    Calculate descriptive statistics.
    """

    if (
        df.empty
        or score_column not in df.columns
    ):
        return pd.DataFrame()

    values = (
        pd.to_numeric(
            df[score_column],
            errors="coerce",
        )
        .dropna()
    )

    if values.empty:
        return pd.DataFrame()

    n = len(values)

    mean = values.mean()

    median = values.median()

    sd = (
        values.std(ddof=1)
        if n > 1
        else 0.0
    )

    minimum = values.min()

    maximum = values.max()

    if n > 1:

        standard_error = (
            sd / np.sqrt(n)
        )

        ci_margin = (
            1.96 * standard_error
        )

        ci_low = mean - ci_margin

        ci_high = mean + ci_margin

    else:

        ci_low = mean

        ci_high = mean

    return pd.DataFrame(
        {
            "Metric": [
                "N (մասնակիցների քանակ)",
                "Միջին (Mean)",
                "Մեդիան (Median)",
                "Ստանդարտ շեղում (SD)",
                "Նվազագույն արժեք (Minimum)",
                "Առավելագույն արժեք (Maximum)",
                "95% վստահության միջակայքի ստորին սահման",
                "95% վստահության միջակայքի վերին սահման",
            ],
            "Value": [
                n,
                mean,
                median,
                sd,
                minimum,
                maximum,
                ci_low,
                ci_high,
            ],
        }
    )


def grouped_statistics(
    df,
    group_column,
    score_column="total",
):
    """
    Descriptive statistics by group.
    """

    if (
        df.empty
        or group_column not in df.columns
        or score_column not in df.columns
    ):
        return pd.DataFrame()

    result = (
        df.groupby(group_column)[score_column]
        .agg(
            N="count",
            Mean="mean",
            Median="median",
            SD="std",
            Min="min",
            Max="max",
        )
        .reset_index()
    )

    return result


def dimension_statistics(df):

    if df.empty:
        return pd.DataFrame()

    available = [
        column
        for column in SCORE_COLUMNS
        if column in df.columns
    ]

    if not available:
        return pd.DataFrame()

    result = (
        df[available]
        .agg(
            [
                "count",
                "mean",
                "median",
                "std",
                "min",
                "max",
            ]
        )
        .T
        .reset_index()
    )

    result.columns = [
        "Metric",
        "N (մասնակիցների քանակ)",
        "Միջին (Mean)",
        "Մեդիան (Median)",
        "Ստանդարտ շեղում (SD)",
        "Նվազագույն արժեք (Minimum)",
        "Առավելագույն արժեք (Maximum)",
    ]

    return result


# ============================================================
# CROSS ANALYSIS
# ============================================================

def competency_difficulty_table(df):

    if df.empty:
        return pd.DataFrame()

    return pd.pivot_table(
        df,
        values="total",
        index="competency_short",
        columns="difficulty_short",
        aggfunc="mean",
    )


def competency_language_table(df):

    if df.empty:
        return pd.DataFrame()

    return pd.pivot_table(
        df,
        values="total",
        index="competency_short",
        columns="language",
        aggfunc="mean",
    )


def difficulty_language_table(df):

    if df.empty:
        return pd.DataFrame()

    return pd.pivot_table(
        df,
        values="total",
        index="difficulty_short",
        columns="language",
        aggfunc="mean",
    )


# ============================================================
# CORRELATION
# ============================================================

def correlation_analysis(df):

    available = [
        column
        for column in SCORE_COLUMNS
        if column in df.columns
    ]

    if len(available) < 2:
        return pd.DataFrame()

    return df[available].corr(
        method="pearson"
    )


# ============================================================
# PARTICIPANT ANALYSIS
# ============================================================

def participant_analysis(df):

    if (
        df.empty
        or "participant_id" not in df.columns
    ):
        return pd.DataFrame()

    return (
        df.groupby("participant_id")["total"]
        .agg(
            N="count",
            Mean="mean",
            Median="median",
            SD="std",
            Min="min",
            Max="max",
        )
        .reset_index()
    )


# ============================================================
# STATISTICAL TESTS
# ============================================================

def one_way_anova(
    df,
    group_column="competency_short",
):
    """
    One-way ANOVA.

    Exploratory group comparison.
    """

    if (
        df.empty
        or group_column not in df.columns
    ):
        return None

    try:
        from scipy import stats
    except ImportError:
        return None

    groups = []

    for _, group in df.groupby(
        group_column
    ):

        values = (
            pd.to_numeric(
                group["total"],
                errors="coerce",
            )
            .dropna()
            .values
        )

        if len(values) >= 2:
            groups.append(values)

    if len(groups) < 2:
        return None

    statistic, p_value = (
        stats.f_oneway(*groups)
    )

    return {
        "F": float(statistic),
        "p": float(p_value),
    }


def spearman_correlation(
    df,
    x,
    y,
):
    """
    Spearman rank correlation.
    """

    if (
        x not in df.columns
        or y not in df.columns
    ):
        return None

    try:
        from scipy import stats
    except ImportError:
        return None

    values = df[
        [x, y]
    ].dropna()

    if len(values) < 3:
        return None

    coefficient, p_value = (
        stats.spearmanr(
            values[x],
            values[y],
        )
    )

    return {
        "rho": float(coefficient),
        "p": float(p_value),
        "N": len(values),
    }


# ============================================================
# AI × EXPERT ANALYSIS
# ============================================================

def ai_expert_comparison(df):
    """
    Compare AI and independent expert scores.

    This becomes useful once expert evaluations
    are added to the dataset.
    """

    required = [
        "total",
        "expert_total",
    ]

    if any(
        column not in df.columns
        for column in required
    ):
        return pd.DataFrame()

    comparison = df[
        required
    ].dropna()

    if comparison.empty:
        return pd.DataFrame()

    comparison = comparison.copy()

    comparison["difference"] = (
        comparison["ai_total"]
        if "ai_total" in comparison.columns
        else comparison["total"]
    )

    if "expert_total" in comparison.columns:

        comparison["ai_expert_difference"] = (
            comparison["total"]
            - comparison["expert_total"]
        )

        comparison["absolute_difference"] = (
            comparison[
                "ai_expert_difference"
            ].abs()
        )

    return comparison


def ai_expert_dimension_statistics(df):
    """
    Compare AI and expert means for each dimension.
    """

    pairs = [
        (
            "understanding",
            "expert_understanding",
        ),
        (
            "problem_detection",
            "expert_problem_detection",
        ),
        (
            "adaptation",
            "expert_adaptation",
        ),
        (
            "optimization",
            "expert_optimization",
        ),
        (
            "clarity",
            "expert_clarity",
        ),
        (
            "total",
            "expert_total",
        ),
    ]

    rows = []

    for ai_column, expert_column in pairs:

        if (
            ai_column not in df.columns
            or expert_column not in df.columns
        ):
            continue

        values = df[
            [
                ai_column,
                expert_column,
            ]
        ].dropna()

        if values.empty:
            continue

        rows.append(
            {
                "Dimension": ai_column,
                "N": len(values),
                "AI Mean": values[
                    ai_column
                ].mean(),
                "Expert Mean": values[
                    expert_column
                ].mean(),
                "Mean Difference": (
                    values[ai_column].mean()
                    - values[
                        expert_column
                    ].mean()
                ),
                "MAE": (
                    (
                        values[ai_column]
                        - values[
                            expert_column
                        ]
                    )
                    .abs()
                    .mean()
                ),
            }
        )

    return pd.DataFrame(rows)


# ============================================================
# CSV EXPORT
# ============================================================

def dataframe_to_csv(df):
    """
    UTF-8 CSV suitable for Excel.
    """

    return df.to_csv(
        index=False
    ).encode("utf-8-sig")


# ============================================================
# FORMATTING
# ============================================================

def _round_dataframe(df):

    result = df.copy()

    for column in result.columns:

        if pd.api.types.is_numeric_dtype(
            result[column]
        ):

            result[column] = (
                result[column]
                .round(3)
            )

    return result


# ============================================================
# RESEARCH DASHBOARD
# ============================================================

def render_research_dashboard(
    all_results,
):
    """
    Main research analytics interface.

    Call this from app.py.
    """

    st.markdown(
        "##  Research Analytics"
    )

    st.caption(
        "AI Code Lab — գիտական վիճակագրական "
        "վերլուծության և տվյալների ուսումնասիրության բաժին"
    )

    # ========================================================
    # DATASET
    # ========================================================

    df = build_research_dataframe(
        all_results
    )

    if df.empty:

        st.info(
            "Դեռ պահպանված հետազոտական տվյալներ չկան։"
        )

        st.markdown(
            """
### Վերլուծությունը կներառի

- Descriptive statistics
- Competency analysis
- Difficulty analysis
- Programming language analysis
- Competency × Difficulty
- Competency × Language
- Multidimensional score analysis
- Correlation analysis
- Participant-level analysis
- ANOVA
- Spearman correlation
- Task և Student Solution տվյալների export
- Future AI × Expert comparison
            """
        )

        return

    # ========================================================
    # FILTERS
    # ========================================================

    st.markdown(
        "### 🎛️ Analysis Filters"
    )

    f1, f2, f3 = st.columns(3)

    competencies = sorted(
        df["competency_short"]
        .dropna()
        .unique()
        .tolist()
    )

    difficulties = sorted(
        df["difficulty_short"]
        .dropna()
        .unique()
        .tolist()
    )

    languages = sorted(
        df["language"]
        .dropna()
        .unique()
        .tolist()
    )

    with f1:

        selected_competencies = (
            st.multiselect(
                "Կոմպետենտություն",
                competencies,
                default=competencies,
            )
        )

    with f2:

        selected_difficulties = (
            st.multiselect(
                "Բարդություն",
                difficulties,
                default=difficulties,
            )
        )

    with f3:

        selected_languages = (
            st.multiselect(
                "Ծրագրավորման լեզու",
                languages,
                default=languages,
            )
        )

    filtered_df = df[
        df["competency_short"].isin(
            selected_competencies
        )
        &
        df["difficulty_short"].isin(
            selected_difficulties
        )
        &
        df["language"].isin(
            selected_languages
        )
    ].copy()

    if filtered_df.empty:

        st.warning(
            "Ընտրված ֆիլտրերով տվյալներ չկան։"
        )

        return

    # ========================================================
    # DATASET OVERVIEW
    # ========================================================

    st.divider()

    st.markdown(
        "### 📊 Dataset Overview"
    )

    participants = (
        filtered_df[
            "participant_id"
        ].nunique()
    )

    observations = len(
        filtered_df
    )

    tasks = (
        filtered_df[
            "task_id"
        ].nunique()
    )

    mean_score = (
        filtered_df["total"]
        .mean()
    )

    median_score = (
        filtered_df["total"]
        .median()
    )

    c1, c2, c3, c4, c5 = (
        st.columns(5)
    )

    c1.metric(
        "Participants",
        participants,
    )

    c2.metric(
        "Observations",
        observations,
    )

    c3.metric(
        "Tasks",
        tasks,
    )

    c4.metric(
        "Mean",
        f"{mean_score:.2f}",
    )

    c5.metric(
        "Median",
        f"{median_score:.2f}",
    )

    # ========================================================
    # DESCRIPTIVE STATISTICS
    # ========================================================

    st.divider()

    st.markdown(
        "### 📐 Descriptive Statistics"
    )

    desc = descriptive_statistics(
        filtered_df
    )

    if not desc.empty:

        st.dataframe(
            _round_dataframe(desc),
            use_container_width=True,
            hide_index=True,
        )

    st.caption(
        "95% confidence interval-ը ներկայացվում է "
        "որպես մոտարկված interval և պետք է "
        "զգուշությամբ մեկնաբանվի փոքր ընտրանքների դեպքում։"
    )

    # ========================================================
    # COMPETENCY
    # ========================================================

    st.divider()

    st.markdown(
        "### 🔍 Competency Analysis"
    )

    competency_stats = grouped_statistics(
        filtered_df,
        "competency_short",
    )

    if not competency_stats.empty:

        st.dataframe(
            _round_dataframe(
                competency_stats
            ),
            use_container_width=True,
            hide_index=True,
        )

        chart_df = (
            competency_stats[
                [
                    "competency_short",
                    "Mean",
                ]
            ]
            .set_index(
                "competency_short"
            )
        )

        st.bar_chart(
            chart_df
        )

    # ========================================================
    # MULTIDIMENSIONAL
    # ========================================================

    st.divider()

    st.markdown(
        "### 🧩 Multidimensional Competency Analysis"
    )

    dimensions = dimension_statistics(
        filtered_df
    )

    if not dimensions.empty:

        st.dataframe(
            _round_dataframe(
                dimensions
            ),
            use_container_width=True,
            hide_index=True,
        )

        dimension_chart = (
            dimensions[
                [
                    "Metric",
                    "Միջին (Mean)",
                ]
            ]
            .set_index("Metric")
        )

        st.bar_chart(
            dimension_chart
        )

    # ========================================================
    # DIFFICULTY
    # ========================================================

    st.divider()

    st.markdown(
        "### 🎯 Difficulty Analysis"
    )

    difficulty_stats = grouped_statistics(
        filtered_df,
        "difficulty_short",
    )

    if not difficulty_stats.empty:

        st.dataframe(
            _round_dataframe(
                difficulty_stats
            ),
            use_container_width=True,
            hide_index=True,
        )

        st.bar_chart(
            difficulty_stats.set_index(
                "difficulty_short"
            )["Mean"]
        )

    # ========================================================
    # LANGUAGE
    # ========================================================

    st.divider()

    st.markdown(
        "### 💻 Programming Language Analysis"
    )

    language_stats = grouped_statistics(
        filtered_df,
        "language",
    )

    if not language_stats.empty:

        st.dataframe(
            _round_dataframe(
                language_stats
            ),
            use_container_width=True,
            hide_index=True,
        )

        st.bar_chart(
            language_stats.set_index(
                "language"
            )["Mean"]
        )

    # ========================================================
    # COMPETENCY × DIFFICULTY
    # ========================================================

    st.divider()

    st.markdown(
        "### 🔀 Competency × Difficulty"
    )

    cross_difficulty = (
        competency_difficulty_table(
            filtered_df
        )
    )

    if not cross_difficulty.empty:

        st.dataframe(
            cross_difficulty.round(2),
            use_container_width=True,
        )

        st.bar_chart(
            cross_difficulty
        )

    # ========================================================
    # COMPETENCY × LANGUAGE
    # ========================================================

    st.divider()

    st.markdown(
        "### 🔀 Competency × Language"
    )

    cross_language = (
        competency_language_table(
            filtered_df
        )
    )

    if not cross_language.empty:

        st.dataframe(
            cross_language.round(2),
            use_container_width=True,
        )

        st.bar_chart(
            cross_language
        )

    # ========================================================
    # DIFFICULTY × LANGUAGE
    # ========================================================

    st.divider()

    st.markdown(
        "### 🔀 Difficulty × Language"
    )

    cross_diff_language = (
        difficulty_language_table(
            filtered_df
        )
    )

    if not cross_diff_language.empty:

        st.dataframe(
            cross_diff_language.round(2),
            use_container_width=True,
        )

    # ========================================================
    # CORRELATION
    # ========================================================

    st.divider()

    st.markdown(
        "### 🔗 Correlation Analysis"
    )

    correlation = correlation_analysis(
        filtered_df
    )

    if not correlation.empty:

        st.dataframe(
            correlation.round(3),
            use_container_width=True,
        )

        st.caption(
            "Pearson correlation matrix."
        )

    # ========================================================
    # PARTICIPANTS
    # ========================================================

    st.divider()

    st.markdown(
        "### 👥 Participant-level Analysis"
    )

    participant_stats = (
        participant_analysis(
            filtered_df
        )
    )

    if not participant_stats.empty:

        st.dataframe(
            _round_dataframe(
                participant_stats
            ),
            use_container_width=True,
            hide_index=True,
        )

    # ========================================================
    # ANOVA
    # ========================================================

    st.divider()

    st.markdown(
        "### 🧪 One-way ANOVA"
    )

    anova = one_way_anova(
        filtered_df,
        "competency_short",
    )

    if anova is None:

        st.info(
            "ANOVA-ի համար բավարար տվյալներ չկան "
            "կամ scipy փաթեթը տեղադրված չէ։"
        )

    else:

        a1, a2 = st.columns(2)

        a1.metric(
            "F-statistic",
            f"{anova['F']:.4f}",
        )

        a2.metric(
            "p-value",
            f"{anova['p']:.4f}",
        )

        if anova["p"] < 0.05:

            st.info(
                "p < 0.05․ խմբերի միջինների միջև "
                "վիճակագրական տարբերության ապացույց կա։"
            )

        else:

            st.info(
                "p ≥ 0.05․ վիճակագրական նշանակալի "
                "տարբերություն չի հայտնաբերվել։"
            )

    # ========================================================
    # SPEARMAN
    # ========================================================

    st.divider()

    st.markdown(
        "### 📈 Spearman Correlation"
    )

    correlation_pairs = [
        (
            "understanding",
            "total",
        ),
        (
            "problem_detection",
            "total",
        ),
        (
            "adaptation",
            "total",
        ),
        (
            "optimization",
            "total",
        ),
        (
            "clarity",
            "total",
        ),
    ]

    spearman_rows = []

    for x, y in correlation_pairs:

        result = spearman_correlation(
            filtered_df,
            x,
            y,
        )

        if result:

            spearman_rows.append(
                {
                    "Variable X": x,
                    "Variable Y": y,
                    "N": result["N"],
                    "Spearman rho": result[
                        "rho"
                    ],
                    "p-value": result[
                        "p"
                    ],
                }
            )

    if spearman_rows:

        spearman_df = pd.DataFrame(
            spearman_rows
        )

        st.dataframe(
            _round_dataframe(
                spearman_df
            ),
            use_container_width=True,
            hide_index=True,
        )

    # ========================================================
    # AI × EXPERT
    # ========================================================

    st.divider()

    st.markdown(
        "### 🤖 AI × 👤 Independent Expert"
    )

    expert_comparison = (
        ai_expert_dimension_statistics(
            filtered_df
        )
    )

    if expert_comparison.empty:

        st.info(
            "Independent expert-ի գնահատականներ դեռ "
            "չկան։ Երբ դրանք ավելացվեն dataset-ում, "
            "այստեղ կերևա AI և Expert գնահատականների "
            "համեմատությունը։"
        )

    else:

        st.dataframe(
            _round_dataframe(
                expert_comparison
            ),
            use_container_width=True,
            hide_index=True,
        )

        st.caption(
            "MAE = Mean Absolute Error՝ AI և Expert "
            "գնահատականների բացարձակ տարբերության միջինը։"
        )

    # ========================================================
    # RAW DATA
    # ========================================================

    st.divider()

    st.markdown(
        "### 🗂️ Research Dataset"
    )

    st.caption(
        "Dataset-ում ներառված են նաև ամբողջ "
        "առաջադրանքը և ուսանողի ներկայացրած լուծումը։"
    )

    st.dataframe(
        filtered_df,
        use_container_width=True,
        hide_index=True,
    )

    # ========================================================
    # EXPORT
    # ========================================================

    st.divider()

    st.markdown(
        "### 📥 Export"
    )

    export_col1, export_col2 = (
        st.columns(2)
    )

    # --------------------------------------------------------
    # FILTERED DATA
    # --------------------------------------------------------

    raw_csv = dataframe_to_csv(
        filtered_df
    )

    with export_col1:

        st.download_button(
            label=(
                "📥 Ներբեռնել Research Dataset CSV"
            ),
            data=raw_csv,
            file_name=(
                "ai_code_lab_research_dataset.csv"
            ),
            mime="text/csv",
            use_container_width=True,
            key="download_research_dataset",
        )

    # --------------------------------------------------------
    # COMPETENCY STATISTICS
    # --------------------------------------------------------

    statistics_csv = dataframe_to_csv(
        competency_stats
    )

    with export_col2:

        st.download_button(
            label=(
                "📊 Ներբեռնել Statistics CSV"
            ),
            data=statistics_csv,
            file_name=(
                "ai_code_lab_competency_statistics.csv"
            ),
            mime="text/csv",
            use_container_width=True,
            key="download_statistics",
        )

    # ========================================================
    # FULL RAW DATA
    # ========================================================

    st.markdown(
        "### 📦 Full Dataset"
    )

    st.caption(
        "Այս CSV-ն պարունակում է բոլոր observations-ը՝ "
        "ներառյալ task-ը, student solution-ը և AI evaluation-ը։"
    )

    full_csv = dataframe_to_csv(
        df
    )

    st.download_button(
        label=(
            "⬇️ Ներբեռնել ամբողջ հետազոտական dataset-ը"
        ),
        data=full_csv,
        file_name=(
            "ai_code_lab_full_dataset.csv"
        ),
        mime="text/csv",
        use_container_width=True,
        key="download_full_dataset",
    )