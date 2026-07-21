import streamlit as st
from datetime import datetime
from knowledge_base import KNOWLEDGE_BASE
from matcher import find_best_match, find_top_matches
from doc_search import extract_text_from_pdf, chunk_text, find_best_chunk

st.set_page_config(
    page_title="EDA Assistant | Enchanted Digital Academy",
    page_icon="✨",
    layout="centered",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------
# STYLE
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
    .doc-pill {
        display: inline-block;
        background: #3A2A55;
        color: #C99CE8 !important;
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
            "Ask me anything, like *\"How do I register?\"* or *\"What is EDSIP?\"* "
            "You can also upload a PDF in the sidebar and ask questions about it."
        ),
        "timestamp": datetime.now().strftime("%H:%M")
    })

if "question_log" not in st.session_state:
    # Structured log for the admin dashboard: each entry records the question,
    # whether it was answered, matched category (if any), and source (kb/doc/none)
    st.session_state.question_log = []

if "doc_chunks" not in st.session_state:
    st.session_state.doc_chunks = []
    st.session_state.doc_name = None

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
    st.markdown("**📄 Ask about a document**")
    uploaded_file = st.file_uploader("Upload a PDF", type=["pdf"], label_visibility="collapsed")
    if uploaded_file is not None and uploaded_file.name != st.session_state.doc_name:
        with st.spinner("Reading document..."):
            text = extract_text_from_pdf(uploaded_file)
            st.session_state.doc_chunks = chunk_text(text)
            st.session_state.doc_name = uploaded_file.name
        st.success(f"Loaded: {uploaded_file.name}")
    elif st.session_state.doc_name:
        st.caption(f"📎 Active: {st.session_state.doc_name}")
        if st.button("Remove document", use_container_width=True):
            st.session_state.doc_chunks = []
            st.session_state.doc_name = None
            st.rerun()

    st.divider()
    if st.button("🗑️ Clear conversation", use_container_width=True):
        st.session_state.messages = []
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
    avatar = "✨" if msg["role"] == "assistant" else None
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"], unsafe_allow_html=True)

# ---------------------------------------------------------------
# HANDLE INPUT
# ---------------------------------------------------------------
user_input = st.chat_input("Ask about EDA programs, EDSIP, registration, or your uploaded PDF...")

if "pending_question" in st.session_state:
    user_input = st.session_state.pending_question
    del st.session_state.pending_question

if user_input:
    st.session_state.messages.append({
        "role": "user",
        "content": user_input,
        "timestamp": datetime.now().strftime("%H:%M")
    })

    with st.chat_message("user"):
        st.markdown(user_input)

    match, score = find_best_match(user_input)
    log_entry = {
        "question": user_input,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "answered": False,
        "category": None,
        "source": "none",
    }

    if match:
        response = f"{match['answer']}\n\n<span class='category-pill'>{match['category']}</span>"
        log_entry.update({"answered": True, "category": match["category"], "source": "knowledge_base"})
    else:
        # Try the uploaded document next, if there is one
        doc_chunk, doc_score = (None, 0.0)
        if st.session_state.doc_chunks:
            doc_chunk, doc_score = find_best_chunk(user_input, st.session_state.doc_chunks)

        if doc_chunk:
            response = (
                f"Based on your uploaded document (**{st.session_state.doc_name}**), here's the most relevant part:\n\n"
                f"> {doc_chunk.strip()}\n\n<span class='doc-pill'>From uploaded document</span>"
            )
            log_entry.update({"answered": True, "category": "Uploaded Document", "source": "document"})
        else:
            suggestions = find_top_matches(user_input, n=3, threshold=0.15)
            base_message = (
                "I couldn't find a specific answer to that question. Please contact the EDA team via "
                "**hello@enchanteddigitalacademy.com.ng** or WhatsApp **+234 706 586 2449**. "
                "You can also ask another question about our programs, internships, registration, or mentorship."
            )
            if suggestions:
                sug_text = "\n".join([f"- {e['question']}" for e, s in suggestions])
                response = f"{base_message}\n\nHere are a few related questions I can help with:\n\n{sug_text}"
            else:
                response = base_message

    st.session_state.question_log.append(log_entry)

    st.session_state.messages.append({
        "role": "assistant",
        "content": response,
        "timestamp": datetime.now().strftime("%H:%M")
    })

    with st.chat_message("assistant", avatar="✨"):
        st.markdown(response, unsafe_allow_html=True)
