from pathlib import Path

import duckdb
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="AI Trivia Benchmark",
    page_icon="📊",
    layout="wide",
)

DB_PATH = Path(__file__).resolve().parent / "warehouse" / "benchmark.duckdb"


def load_results():
    with duckdb.connect(str(DB_PATH), read_only=True) as con:
        return con.execute(
            "SELECT * FROM main.int_benchmark_results"
        ).fetchdf()


st.title("AI Trivia Benchmark")

if not DB_PATH.exists():
    st.error(f"Database missing: {DB_PATH}")
    st.stop()

df = load_results()

st.sidebar.header("Filters")

categories = st.sidebar.multiselect(
    "Category",
    sorted(df["category"].dropna().unique().tolist()),
)

difficulties = st.sidebar.multiselect(
    "Difficulty",
    ["easy", "medium", "hard"],
)

question_types = st.sidebar.multiselect(
    "Question type",
    sorted(df["type"].dropna().unique().tolist()),
)

filtered = df.copy()

if categories:
    filtered = filtered[filtered["category"].isin(categories)]

if difficulties:
    filtered = filtered[filtered["difficulty"].isin(difficulties)]

if question_types:
    filtered = filtered[filtered["type"].isin(question_types)]

st.sidebar.caption("Empty selection → all values")

if filtered.empty:
    st.info("No questions match selected filters.")
    st.stop()

evaluated = filtered[filtered["is_evaluated"].fillna(False)].copy()
evaluated["score"] = evaluated["ai_correct"].astype(int)

total = len(filtered)
count = len(evaluated)
correct = int(evaluated["score"].sum())
accuracy = correct / count * 100 if count else None

timings = evaluated["response_time"].dropna()
avg_time = timings.mean() if not timings.empty else None
median_time = timings.median() if not timings.empty else None

col1, col2, col3, col4 = st.columns(4)

col1.metric("Questions", f"{total:,}")
col2.metric(
    "Accuracy",
    f"{accuracy:.2f}%" if accuracy is not None else "N/A",
)
col3.metric(
    "Average response",
    f"{avg_time:.3f} s" if avg_time is not None else "N/A",
)
col4.metric(
    "Median response",
    f"{median_time:.3f} s" if median_time is not None else "N/A",
)

st.caption(
    f"Evaluated: {count:,} | Correct: {correct:,} | "
    f"Unevaluated: {total - count:,}. "
    "Accuracy calculated among evaluated questions."
)


def summarize(column):
    summary = evaluated.groupby(column, dropna=False).agg(
        evaluated_questions=("score", "size"),
        correct_answers=("score", "sum"),
        accuracy_pct=("score", "mean"),
        avg_response_time=("response_time", "mean"),
    )
    summary["accuracy_pct"] *= 100
    return summary


if count:
    left, right = st.columns(2)

    with left:
        st.subheader("Accuracy by category")
        by_category = summarize("category").sort_values("accuracy_pct")
        st.bar_chart(
            by_category[["accuracy_pct"]],
            horizontal=True,
        )
        st.dataframe(by_category, use_container_width=True)

    with right:
        st.subheader("Accuracy by difficulty")
        by_difficulty = summarize("difficulty").reindex(
            ["easy", "medium", "hard"]
        ).dropna(subset=["evaluated_questions"])

        st.bar_chart(by_difficulty[["accuracy_pct"]])
        st.dataframe(by_difficulty, use_container_width=True)

    st.subheader("Response time distribution")

    if not timings.empty:
        bins = pd.cut(timings, bins=20)
        distribution = (
            bins.value_counts(sort=False)
            .rename_axis("Response time interval")
            .reset_index(name="Questions")
        )
        distribution["Response time interval"] = (
            distribution["Response time interval"].astype(str)
        )
        st.bar_chart(
            distribution.set_index("Response time interval")
        )
else:
    st.info("No evaluated questions in this selection.")

st.subheader("Question explorer")

result_filter = st.selectbox(
    "Result",
    ["All", "Correct", "Incorrect", "Unevaluated"],
)

questions = filtered.copy()
is_evaluated = questions["is_evaluated"].fillna(False)

if result_filter == "Correct":
    questions = questions[
        is_evaluated & questions["ai_correct"].fillna(False)
    ]
elif result_filter == "Incorrect":
    questions = questions[
        is_evaluated & ~questions["ai_correct"].fillna(False)
    ]
elif result_filter == "Unevaluated":
    questions = questions[~is_evaluated]

search = st.text_input("Search question")

if search:
    questions = questions[
        questions["question"].str.contains(
            search,
            case=False,
            regex=False,
            na=False,
        )
    ]

columns = [
    "category",
    "difficulty",
    "question",
    "correct_answer",
    "ai_answer",
    "ai_correct",
    "response_time",
]

st.dataframe(
    questions[columns],
    use_container_width=True,
    hide_index=True,
)

st.download_button(
    "Download displayed questions",
    data=questions[columns].to_csv(index=False).encode("utf-8"),
    file_name="benchmark_questions.csv",
    mime="text/csv",
)