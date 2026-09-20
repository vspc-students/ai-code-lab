# charts.py

import pandas as pd
import streamlit as st
import plotly.graph_objects as go



# ---------------------------------------------------------
# DATA
# ---------------------------------------------------------

def _rows(results):
    rows = []

    for item in results:
        evaluation = item.get("evaluation", {})

        difficulty = item.get("difficulty", "")
        competency = item.get("competency", "")

        difficulty = difficulty.split(" / ")[0]
        competency = competency.split(" / ")[0]

        rows.append({
            "Task": item.get("task_id", ""),
            "Difficulty": difficulty,
            "Competency": competency,
            "Total": evaluation.get("total", 0),
            "Understanding": evaluation.get("understanding", 0),
            "Detection": evaluation.get("problem_detection", 0),
            "Adaptation": evaluation.get("adaptation", 0),
            "Optimization": evaluation.get("optimization", 0),
        })

    return pd.DataFrame(rows)


# ---------------------------------------------------------
# 1. COMPETENCY PROFILE
# ---------------------------------------------------------

def render_competency_chart(results):

    df = _rows(results)

    if df.empty:
        return

    st.markdown("###  Կոմպետենտության պրոֆիլ")
    st.caption(
        "Մասնակցի հիմնական ծրագրավորման կոմպետենտությունների "
        "միջին գնահատականները՝ 0–100 սանդղակով։"
    )

    competency_order = [
        "Կոդի ընկալում",
        "Սխալի հայտնաբերում և ուղղում",
        "Կոդի ադապտացում",
        "Կոդի օպտիմալացում",
    ]

    profile = []

    for competency in competency_order:

        values = df.loc[
            df["Competency"] == competency,
            "Total"
        ]

        if not values.empty:
            profile.append({
                "Competency": competency,
                "Score": round(values.mean(), 1),
                "Tasks": len(values),
            })

    if not profile:
        st.info("Կոմպետենտությունների տվյալներ դեռ չկան։")
        return

    profile_df = pd.DataFrame(profile)

    # -----------------------------------------------------
    # HORIZONTAL BAR
    # -----------------------------------------------------

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=profile_df["Score"],
            y=profile_df["Competency"],
            orientation="h",
            text=[
                f"{value:.0f}/100"
                for value in profile_df["Score"]
            ],
            textposition="outside",
            hovertemplate=(
                "<b>%{y}</b><br>"
                "Գնահատական՝ %{x:.1f}/100"
                "<extra></extra>"
            ),
        )
    )

    fig.update_layout(
        height=420,
        margin=dict(
            l=20,
            r=80,
            t=20,
            b=30,
        ),
        xaxis=dict(
            range=[0, 100],
            dtick=20,
            title="Գնահատական / 100",
            gridcolor="rgba(128,128,128,0.18)",
            zeroline=False,
        ),
        yaxis=dict(
            title="",
            autorange="reversed",
        ),
        showlegend=False,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        config={
            "displayModeBar": False,
            "responsive": True,
        },
    )


# ---------------------------------------------------------
# 2. RADAR / SPIDER PROFILE
# ---------------------------------------------------------

def render_competency_radar(results):

    df = _rows(results)

    if df.empty:
        return

    competency_order = [
        "Կոդի ընկալում",
        "Սխալի հայտնաբերում և ուղղում",
        "Կոդի ադապտացում",
        "Կոդի օպտիմալացում",
    ]

    scores = []

    for competency in competency_order:

        values = df.loc[
            df["Competency"] == competency,
            "Total"
        ]

        if values.empty:
            scores.append(0)
        else:
            scores.append(round(values.mean(), 1))

    # Փակում ենք radar polygon-ը
    radar_labels = competency_order + [competency_order[0]]
    radar_scores = scores + [scores[0]]

    fig = go.Figure()

    fig.add_trace(
        go.Scatterpolar(
            r=radar_scores,
            theta=radar_labels,
            fill="toself",
            text=[
                f"{score}/100"
                for score in radar_scores
            ],
            hovertemplate=(
                "<b>%{theta}</b><br>"
                "Գնահատական՝ %{r}/100"
                "<extra></extra>"
            ),
            line=dict(
                width=3
            ),
            opacity=0.85,
        )
    )

    fig.update_layout(
        height=560,
        margin=dict(
            l=70,
            r=70,
            t=40,
            b=40,
        ),
        polar=dict(

            bgcolor="rgba(0,0,0,0)",

            radialaxis=dict(
                visible=True,
                range=[0, 100],
                dtick=20,
                gridcolor="rgba(128,128,128,0.22)",
                linecolor="rgba(128,128,128,0.25)",
                tickfont=dict(size=11),
            ),

            angularaxis=dict(
                gridcolor="rgba(128,128,128,0.18)",
                linecolor="rgba(128,128,128,0.25)",
                tickfont=dict(size=13),
            ),
        ),

        showlegend=False,

        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        config={
            "displayModeBar": False,
            "responsive": True,
        },
    )


# ---------------------------------------------------------
# 3. DIFFICULTY × COMPETENCY HEATMAP
# ---------------------------------------------------------

def render_difficulty_heatmap(results):

    df = _rows(results)

    if df.empty:
        return

    st.markdown("### 🔥 Կոմպետենտություն × Բարդություն")
    st.caption(
        "Ցույց է տալիս, թե ինչպես է փոխվում արդյունքը "
        "Easy → Medium → Hard մակարդակներում։"
    )

    difficulty_order = [
        "Easy",
        "Medium",
        "Hard",
    ]

    competency_order = [
        "Կոդի ընկալում",
        "Սխալի հայտնաբերում և ուղղում",
        "Կոդի ադապտացում",
        "Կոդի օպտիմալացում",
    ]

    matrix = []

    for competency in competency_order:

        row = []

        for difficulty in difficulty_order:

            values = df.loc[
                (df["Competency"] == competency)
                &
                (df["Difficulty"] == difficulty),
                "Total"
            ]

            if values.empty:
                row.append(None)
            else:
                row.append(round(values.mean(), 1))

        matrix.append(row)

    fig = go.Figure(
        data=go.Heatmap(
            z=matrix,
            x=difficulty_order,
            y=competency_order,
            zmin=0,
            zmax=100,
            text=[
                [
                    "—" if value is None
                    else f"{value:.0f}"
                    for value in row
                ]
                for row in matrix
            ],
            texttemplate="%{text}",
            textfont=dict(size=16),
            hovertemplate=(
                "<b>%{y}</b><br>"
                "Բարդություն՝ %{x}<br>"
                "Միջին գնահատական՝ %{z:.1f}/100"
                "<extra></extra>"
            ),
            colorbar=dict(
                title="Score"
            ),
        )
    )

    fig.update_layout(
        height=430,
        margin=dict(
            l=20,
            r=20,
            t=20,
            b=40,
        ),
        xaxis=dict(
            title="Բարդության մակարդակ",
        ),
        yaxis=dict(
            title="",
            autorange="reversed",
        ),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        config={
            "displayModeBar": False,
            "responsive": True,
        },
    )


# ---------------------------------------------------------
# 4. PROGRESS / ATTEMPTS
# ---------------------------------------------------------

def render_task_chart(results):

    df = _rows(results)

    if df.empty:
        return

    st.markdown("### 📈 Փորձերի դինամիկա")

    st.caption(
        "Մասնակցի արդյունքների փոփոխությունը "
        "առաջադրանքների կատարման հերթականությամբ։"
    )

    df = df.reset_index(drop=True)

    df["Attempt"] = range(1, len(df) + 1)

    # Յուրաքանչյուր կետի համար առանձին hover text
    hover_text = []

    for _, row in df.iterrows():

        hover_text.append(
            f"<b>Փորձ {row['Attempt']}</b><br>"
            f"Գնահատական՝ {row['Total']}/100<br>"
            f"Կոմպետենտություն՝ {row['Competency']}<br>"
            f"Բարդություն՝ {row['Difficulty']}"
        )

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=df["Attempt"],
            y=df["Total"],
            mode="lines+markers+text",
            text=[
                f"{score}"
                for score in df["Total"]
            ],
            textposition="top center",

            hovertext=hover_text,
            hovertemplate=(
                "%{hovertext}"
                "<extra></extra>"
            ),

            line=dict(
                width=3
            ),

            marker=dict(
                size=10
            ),
        )
    )

    fig.update_layout(

        height=400,

        margin=dict(
            l=20,
            r=20,
            t=30,
            b=50,
        ),

        xaxis=dict(
            title="Փորձի հերթականություն",
            dtick=1,
        ),

        yaxis=dict(
            title="Գնահատական / 100",
            range=[0, 100],
            dtick=20,
            gridcolor="rgba(128,128,128,0.18)",
        ),

        showlegend=False,

        plot_bgcolor="rgba(0,0,0,0)",

        paper_bgcolor="rgba(0,0,0,0)",
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        config={
            "displayModeBar": False,
            "responsive": True,
        },
    )


# ---------------------------------------------------------
# 5. SUMMARY CARDS
# ---------------------------------------------------------

def render_summary(results):

    df = _rows(results)

    if df.empty:
        return

    total_average = round(df["Total"].mean(), 1)
    highest = int(df["Total"].max())
    lowest = int(df["Total"].min())
    attempts = len(df)

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Միջին արդյունք",
        f"{total_average}/100"
    )

    c2.metric(
        "Լավագույն արդյունք",
        f"{highest}/100"
    )

    c3.metric(
        "Նվազագույն արդյունք",
        f"{lowest}/100"
    )

    c4.metric(
        "Փորձերի քանակ",
        attempts
    )