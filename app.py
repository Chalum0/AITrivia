from pathlib import Path

import duckdb
import pandas as pd
import streamlit as st

st.set_page_config(page_title="AI Trivia · Prompt Lab", page_icon="◈", layout="wide")
ROOT = Path(__file__).resolve().parent
DB_PATH = ROOT / "warehouse" / "benchmark.duckdb"
COLORS = ["#64748b", "#14b8a6"]

st.markdown("""
<style>
.block-container {max-width:1400px;padding-top:2.5rem;padding-bottom:3rem;}
[data-testid="stMetric"] {border:1px solid #94a3b833;border-radius:16px;padding:20px;background:#94a3b808;}
[data-testid="stMetricLabel"] {font-size:0.85rem;}
h1 {letter-spacing:-0.045em;}
h2,h3 {letter-spacing:-0.025em;}
[data-testid="stSidebar"] {border-right:1px solid #94a3b822;}
</style>
""", unsafe_allow_html=True)


def load_data():
    with duckdb.connect(str(DB_PATH), read_only=True) as con:
        rows = con.sql("select * from main.int_benchmark_results").fetchdf()
        gold = con.sql("select * from main.mart_overall_performance").fetchdf()
    return rows, gold


def pct(series):
    return float(series.astype(int).mean() * 100) if len(series) else None


def display_pct(value):
    return "N/A" if value is None or pd.isna(value) else f"{value:.2f}%"


def compare_by(data, column):
    result = data.groupby(column, dropna=False).agg(
        Questions=("ai_correct", "size"),
        Original=("ai_correct", "mean"),
        Instructed=("ai_correct_instructed", "mean"),
    )
    result[["Original", "Instructed"]] *= 100
    result["Gain (pp)"] = result["Instructed"] - result["Original"]
    return result


st.caption("AI TRIVIA / PROMPT LAB")
st.title("Small prompt. Measurable difference.")
st.write("Compare original and instructed answers across the same trivia questions.")

if not DB_PATH.exists():
    st.error("Database missing. Place app.py at project root and run build_gold.py first.")
    st.stop()
try:
    df, gold = load_data()
except duckdb.Error as error:
    st.error(f"Could not read benchmark. Rebuild Gold. Details: {error}")
    st.stop()

required = {"ai_answer_instructed", "ai_correct_instructed", "is_evaluated_instructed"}
if not required.issubset(df.columns):
    st.error("Instructed columns missing from intermediate model. Update SQL, then run build_gold.py.")
    st.stop()
for column in ["ai_correct", "ai_correct_instructed", "is_evaluated", "is_evaluated_instructed"]:
    df[column] = df[column].astype("boolean")

with st.sidebar:
    st.title("◈ Prompt Lab")
    st.caption("BENCHMARK FILTERS")
    categories = st.multiselect("Categories", sorted(df.category.dropna().unique()))
    difficulties = st.multiselect("Difficulty", ["easy", "medium", "hard"])
    types = st.multiselect("Question type", sorted(df.type.dropna().unique()))
    st.caption("Empty selection includes all values.")
    st.button("Refresh data", help="Every interaction reloads the database.")

filtered = df.copy()
for column, values in [("category", categories), ("difficulty", difficulties), ("type", types)]:
    if values:
        filtered = filtered[filtered[column].isin(values)]
if filtered.empty:
    st.info("No questions match these filters.")
    st.stop()

original_mask = filtered.is_evaluated.fillna(False)
instructed_mask = filtered.is_evaluated_instructed.fillna(False)
paired = filtered[original_mask & instructed_mask].copy()
original_accuracy = pct(paired.ai_correct)
instructed_accuracy = pct(paired.ai_correct_instructed)
gain = instructed_accuracy - original_accuracy if len(paired) else None

c1, c2, c3, c4 = st.columns(4)
c1.metric("Shared evaluated questions", f"{len(paired):,}")
c2.metric("Original accuracy", display_pct(original_accuracy))
c3.metric("Instructed accuracy", display_pct(instructed_accuracy))
c4.metric("Prompt gain", f"{gain:+.2f} pp" if gain is not None else "N/A")
st.caption(f"Selected questions: {len(filtered):,} · Original evaluated: {int(original_mask.sum()):,} · Instructed evaluated: {int(instructed_mask.sum()):,}. Comparisons use only questions evaluated in both variants. pp = percentage points.")

comparison, explorer, timing, summary = st.tabs(["Prompt comparison", "Answer explorer", "Response times", "Gold summary"])
with comparison:
    if paired.empty:
        st.info("No shared evaluated questions yet.")
    else:
        orig = paired.ai_correct.fillna(False)
        inst = paired.ai_correct_instructed.fillna(False)
        fixed = int((~orig & inst).sum())
        regressed = int((orig & ~inst).sum())
        a, b, c = st.columns(3)
        a.metric("Fixed by instructions", f"{fixed:,}")
        b.metric("Regressed with instructions", f"{regressed:,}")
        c.metric("Unchanged correctness", f"{len(paired)-fixed-regressed:,}")
        st.subheader("Accuracy by difficulty")
        difficulty = compare_by(paired, "difficulty").reindex(["easy", "medium", "hard"]).dropna(subset=["Questions"])
        st.bar_chart(difficulty[["Original", "Instructed"]], color=COLORS, stack=False, y_label="Accuracy (%)")
        st.dataframe(difficulty.round(2), width="stretch")
        st.subheader("Where instructions help most")
        category = compare_by(paired, "category").sort_values("Gain (pp)", ascending=False)
        st.bar_chart(category[["Original", "Instructed"]], color=COLORS, stack=False, horizontal=True, x_label="Accuracy (%)", height=max(350, len(category)*35))
        st.dataframe(category.round(2), width="stretch")

with explorer:
    st.subheader("Both answers. One question.")
    search = st.text_input("Search question", placeholder="Search a topic, name or phrase…")
    outcome = st.selectbox("Comparison outcome", ["All", "Fixed by instructions", "Regressed with instructions", "Both correct", "Both incorrect", "Missing evaluation"])
    rows = filtered.copy()
    o = rows.ai_correct.fillna(False)
    i = rows.ai_correct_instructed.fillna(False)
    shared = rows.is_evaluated.fillna(False) & rows.is_evaluated_instructed.fillna(False)
    masks = {"Fixed by instructions": shared & ~o & i, "Regressed with instructions": shared & o & ~i, "Both correct": shared & o & i, "Both incorrect": shared & ~o & ~i, "Missing evaluation": ~shared}
    if outcome in masks:
        rows = rows[masks[outcome]]
    if search:
        rows = rows[rows.question.str.contains(search, case=False, regex=False, na=False)]
    columns = ["category", "difficulty", "question", "correct_answer", "ai_answer", "ai_correct", "ai_answer_instructed", "ai_correct_instructed"]
    st.caption(f"{len(rows):,} matching questions")
    st.dataframe(rows[columns], width="stretch", hide_index=True, column_config={"ai_answer": "Original answer", "ai_answer_instructed": "Instructed answer", "ai_correct": "Original correct", "ai_correct_instructed": "Instructed correct"})
    if not rows.empty:
        position = st.selectbox("Inspect question", range(len(rows)), format_func=lambda n: f"{n+1}. {str(rows.iloc[n]['question'])[:110]}")
        row = rows.iloc[position]
        with st.container(border=True):
            st.markdown(f"**{row['question']}**")
            st.caption(f"{row['category']} · {row['difficulty']}")
            st.write("Correct answer:", row["correct_answer"])
            left, right = st.columns(2)
            for panel, label, answer, correct, evaluated in [(left, "Original", "ai_answer", "ai_correct", "is_evaluated"), (right, "Instructed", "ai_answer_instructed", "ai_correct_instructed", "is_evaluated_instructed")]:
                with panel:
                    st.markdown(f"**{label}**")
                    st.write(row[answer] if pd.notna(row[answer]) else "No answer")
                    if pd.isna(row[evaluated]) or not bool(row[evaluated]):
                        st.info("Unevaluated")
                    elif bool(row[correct]):
                        st.success("Correct")
                    else:
                        st.error("Incorrect")
    st.download_button("Export matching questions", rows[columns].to_csv(index=False).encode("utf-8"), "prompt_comparison.csv", "text/csv")

with timing:
    st.subheader("Original response times")
    st.caption("Instructed timing was not recorded in current model. Speed comparison unavailable.")
    times = pd.to_numeric(filtered.loc[original_mask, "response_time"], errors="coerce").dropna()
    times = times[times >= 0]
    if times.empty:
        st.info("No valid timing data.")
    else:
        a, b, c = st.columns(3)
        a.metric("Mean", f"{times.mean():.3f} s")
        b.metric("Median", f"{times.median():.3f} s")
        c.metric("95th percentile", f"{times.quantile(.95):.3f} s")
        histogram = pd.cut(times, bins=20).value_counts(sort=False)
        histogram.index = histogram.index.astype(str)
        st.bar_chart(histogram.rename("Questions"), color=COLORS[0], x_label="Seconds")

with summary:
    st.subheader("Precomputed Gold metrics")
    st.caption("Full dataset, independent of sidebar filters. Created by dbt.")
    st.dataframe(gold, width="stretch", hide_index=True)
    st.download_button("Export Gold summary", gold.to_csv(index=False).encode("utf-8"), "gold_summary.csv", "text/csv")
