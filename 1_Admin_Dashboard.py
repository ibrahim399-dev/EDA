import streamlit as st
import pandas as pd
from collections import Counter
from knowledge_base import KNOWLEDGE_BASE

st.set_page_config(page_title="Admin Dashboard | EDA Assistant", page_icon="📊", layout="wide")

st.markdown("""
<style>
    .main { background-color: #0F0F24; }
    h1, h2, h3, p, label, span { color: #E8E8F5 !important; }
    div[data-testid="stMetric"] {
        background: #1C1C42;
        border: 1px solid #2A2A55;
        border-radius: 12px;
        padding: 14px 18px;
    }
    section[data-testid="stSidebar"] { background-color: #12122B; }
    section[data-testid="stSidebar"] * { color: #E8E8F5 !important; }
</style>
""", unsafe_allow_html=True)

st.title("📊 EDA Assistant — Admin Dashboard")
st.caption("Live analytics for this session. Password-protect this page before sharing publicly.")

log = st.session_state.get("question_log", [])

if not log:
    st.info("No questions have been asked yet in this session. Chat with the assistant on the main page, then come back here to see analytics.")
    st.stop()

df = pd.DataFrame(log)

# ---------------- TOP METRICS ----------------
col1, col2, col3, col4 = st.columns(4)
total_questions = len(df)
answered = df["answered"].sum()
answer_rate = (answered / total_questions * 100) if total_questions else 0
unique_categories = df["category"].nunique()

col1.metric("Total Questions", total_questions)
col2.metric("Answered", int(answered))
col3.metric("Answer Rate", f"{answer_rate:.0f}%")
col4.metric("Categories Touched", unique_categories)

st.divider()

# ---------------- QUESTIONS BY CATEGORY ----------------
left, right = st.columns(2)

with left:
    st.subheader("Questions by Category")
    cat_counts = df[df["category"].notna()]["category"].value_counts()
    if not cat_counts.empty:
        st.bar_chart(cat_counts)
    else:
        st.caption("No categorized questions yet.")

with right:
    st.subheader("Answer Source Breakdown")
    source_counts = df["source"].value_counts()
    st.bar_chart(source_counts)

st.divider()

# ---------------- UNANSWERED QUESTIONS ----------------
st.subheader("❓ Unanswered Questions")
st.caption("Use these to find gaps in the knowledge base and prioritize new entries.")
unanswered = df[df["answered"] == False]
if not unanswered.empty:
    st.dataframe(
        unanswered[["timestamp", "question"]].rename(columns={"timestamp": "Time", "question": "Question"}),
        use_container_width=True, hide_index=True
    )
else:
    st.success("No unanswered questions this session — great coverage!")

st.divider()

# ---------------- KNOWLEDGE BASE COVERAGE ----------------
st.subheader("📚 Knowledge Base Coverage")
kb_categories = Counter(entry["category"] for entry in KNOWLEDGE_BASE)
kb_df = pd.DataFrame(kb_categories.items(), columns=["Category", "Entries"]).sort_values("Entries", ascending=False)
st.bar_chart(kb_df.set_index("Category"))
st.caption(f"Total entries in knowledge base: {len(KNOWLEDGE_BASE)}")

st.divider()

# ---------------- FULL QUESTION LOG ----------------
st.subheader("🗒️ Full Question Log (this session)")
st.dataframe(
    df.rename(columns={
        "timestamp": "Time", "question": "Question", "answered": "Answered",
        "category": "Category", "source": "Source"
    }),
    use_container_width=True, hide_index=True
)
