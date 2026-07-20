import streamlit as st
from datetime import datetime
from knowledge_base import KNOWLEDGE_BASE
from matcher import find_best_match, find_top_matches

st.set_page_config(
    page_title="EDA Assistant | Enchanted Digital Academy",
    page_icon="✦",
    layout="centered",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------
# STYLE — grounded in EDA's own brand: "bridge" + acceleration hub
# Palette: deep indigo night (#12122B), warm gold accent (#E8A33D)
# signals "African tech acceleration" without generic AI-chat tropes.
# ---------------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Fraunces:wght@500;600&family=Inter:wght@400;500;600&display=swap');

    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    .main { background-color: #0F0F24; }

    .eda-hero {
        background: linear-gradient(135deg, #12122B 0%, #1C1C42 100%);
        border-radius: 16px;
        padding: 28px 24px;
        margin-bottom: 20px;
        border: 1px solid #2A2A55;
    }
    .eda-hero h1 {
        font-family: 'Fraunces', serif;
        font-weight: 600;
        color: #F5F1E8;
        font-size: 1.6rem;
        margin: 0 0 6px 0;
    }
    .eda-hero p {
        color: #B8B8D4;
        font-size: 0.92rem;
        margin: 0;
        line-height: 1.5;
    }
    .eda-badge {
        display: inline-block;
        background: #E8A33D;
        color: #12122B;
        font-size: 0.7rem;
        font-weight: 600;
        padding: 3px 10px;
        border-radius: 20px;
        margin-bottom: 10px;
        letter-spacing: 0.03em;
    }

    .stChatMessage {
        border-radius: 12px;
    }

    section[data-testid="stSidebar"] {
        background-color: #12122B;
        border-right: 1px solid #2A2A55;
    }
    section[data-testid="stSidebar"] * { color: #E8E8F5 !important; }

    .category-pill {
        display: inline-block;
        background: #2A2A55;
        color: #C9A85C !important;
        font-size: 0.72rem;
        padding: 2px 10px;
        border-radius: 20px;
        margin: 2px 4px 2px 0;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------
# SESSION STATE
# ---------------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({
        "role": "assistant",
        "content": (
            "Welcome to **Enchanted Digital Academy** ✦\n\n"
            "I'm your EDA Assistant — here to answer questions about our programs, "
            "EDSIP internships, registration, mentorship, and community.\n\n"
            "Ask me anything, like *\"How do I register?\"* or *\"What is EDSIP?\"*"
        ),
        "timestamp": datetime.now().strftime("%H:%M")
    })

if "unanswered_log" not in st.session_state:
    st.session_state.unanswered_log = []

if "question_log" not in st.session_state:
    st.session_state.question_log = []

# ---------------------------------------------------------------
# SIDEBAR
# ---------------------------------------------------------------
with st.sidebar:
    st.markdown("### ✦ EDA Assistant")
    st.caption("Africa's premier acceleration hub for Branding, PR, and Tech.")
    st.divider()

    st.markdown("**Popular topics**")
    topics = ["What is EDA?", "How do I register?", "What is EDSIP?", "Are programs free?", "How do I become an intern?", "Do you issue certificates?"]
    for t in topics:
        if st.button(t, use_container_width=True, key=f"topic_{t}"):
            st.session_state.pending_question = t

    st.divider()
    if st.button("🗑️ Clear conversation", use_container_width=True):
        st.session_state.messages = []
        st.session_state.unanswered_log = []
        st.session_state.question_log = []
        st.rerun()

    st.divider()
    st.caption(f"Knowledge base: {len(KNOWLEDGE_BASE)} entries")
    st.caption("📍 Lagos, Nigeria")
    st.caption("hello@enchanteddigitalacademy.com.ng")

# ---------------------------------------------------------------
# HERO
# ---------------------------------------------------------------
st.markdown("""
<div class="eda-hero">
    <div class="eda-badge">ASK EDA</div>
    <h1>Where Global Skills Meet African Talent</h1>
    <p>Get instant answers about programs, EDSIP internships, mentorship, and how to get started.</p>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------
# CHAT HISTORY
# ---------------------------------------------------------------
for msg in st.session_state.messages:
    avatar = "✦" if msg["role"] == "assistant" else None
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

# ---------------------------------------------------------------
# HANDLE INPUT (chat box OR sidebar quick-topic click)
# ---------------------------------------------------------------
user_input = st.chat_input("Ask about EDA programs, EDSIP, registration...")

if "pending_question" in st.session_state:
    user_input = st.session_state.pending_question
    del st.session_state.pending_question

if user_input:
    st.session_state.messages.append({
        "role": "user",
        "content": user_input,
        "timestamp": datetime.now().strftime("%H:%M")
    })
    st.session_state.question_log.append(user_input)

    with st.chat_message("user"):
        st.markdown(user_input)

    match, score = find_best_match(user_input)

    if match:
        response = f"{match['answer']}\n\n<span class='category-pill'>{match['category']}</span>"
    else:
        st.session_state.unanswered_log.append(user_input)
        suggestions = find_top_matches(user_input, n=3, threshold=0.15)
        if suggestions:
            sug_text = "\n".join([f"- {e['question']}" for e, s in suggestions])
            response = (
                "I don't have a confident answer for that one yet — but here are a few related "
                f"questions I *can* help with:\n\n{sug_text}\n\n"
                "You can also reach our team directly at **hello@enchanteddigitalacademy.com.ng** "
                "or WhatsApp **+234 706 586 2449** for anything specific."
            )
        else:
            response = (
                "I'm not sure about that one yet — my knowledge is focused on EDA's programs, "
                "EDSIP, registration, and community. For anything outside that, please reach our "
                "team at **hello@enchanteddigitalacademy.com.ng** or WhatsApp **+234 706 586 2449**, "
                "and they'll be happy to help."
            )

    st.session_state.messages.append({
        "role": "assistant",
        "content": response,
        "timestamp": datetime.now().strftime("%H:%M")
    })

    with st.chat_message("assistant", avatar="✦"):
        st.markdown(response, unsafe_allow_html=True)
  
