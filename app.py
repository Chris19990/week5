import streamlit as st

from src.agent.assistant import HealthConnectAssistant


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="HealthConnect Assistant",
    page_icon="✨",
    layout="centered",
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }

    /* Base App Background */
    .stApp {
        background-color: #f4f7f9;
        background-image: radial-gradient(circle at 50% 0%, #ffffff 0%, #f4f7f9 70%);
    }

    /* Glassmorphism Header */
    .main-header {
        background: rgba(255, 255, 255, 0.7);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.5);
        padding: 24px 32px;
        border-radius: 24px;
        margin-bottom: 32px;
        box-shadow: 0 10px 40px -10px rgba(0, 0, 0, 0.08);
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .main-header-text h1 {
        margin: 0;
        font-size: 32px;
        font-weight: 700;
        background: linear-gradient(135deg, #0ea5e9, #3b82f6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: -0.5px;
    }

    .main-header-text p {
        margin: 6px 0 0 0;
        color: #64748b;
        font-size: 15px;
        font-weight: 500;
    }

    /* Status Indicator */
    .status {
        display: flex;
        align-items: center;
        gap: 8px;
        background: rgba(22, 163, 74, 0.1);
        padding: 8px 16px;
        border-radius: 999px;
        color: #16a34a;
        font-size: 13px;
        font-weight: 600;
        border: 1px solid rgba(22, 163, 74, 0.2);
    }

    .status-dot {
        width: 8px;
        height: 8px;
        background-color: #22c55e;
        border-radius: 50%;
        animation: pulse 2s infinite;
    }

    @keyframes pulse {
        0% { box-shadow: 0 0 0 0 rgba(34, 197, 94, 0.4); }
        70% { box-shadow: 0 0 0 8px rgba(34, 197, 94, 0); }
        100% { box-shadow: 0 0 0 0 rgba(34, 197, 94, 0); }
    }

    /* Welcome Card */
    .welcome-card {
        background: white;
        padding: 40px 32px;
        border-radius: 24px;
        border: 1px solid rgba(226, 232, 240, 0.8);
        margin-bottom: 24px;
        box-shadow: 0 20px 40px -20px rgba(0, 0, 0, 0.05);
        text-align: center;
        transition: transform 0.3s ease;
    }

    .welcome-card:hover {
        transform: translateY(-2px);
    }

    .welcome-card h3 {
        color: #0f172a;
        font-size: 28px;
        font-weight: 700;
        margin-bottom: 16px;
        letter-spacing: -0.5px;
    }

    .welcome-card p {
        color: #64748b;
        font-size: 17px;
        line-height: 1.6;
        margin-bottom: 0;
    }

    /* Buttons Overrides */
    div[data-testid="stButton"] button {
        background: white !important;
        color: #334155 !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 14px !important;
        padding: 12px 24px !important;
        font-weight: 500 !important;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02) !important;
        width: 100%;
    }

    div[data-testid="stButton"] button:hover {
        border-color: #0ea5e9 !important;
        color: #0ea5e9 !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 16px rgba(14, 165, 233, 0.12) !important;
    }

    /* Suggested section title */
    .suggested-title {
        font-size: 15px;
        font-weight: 600;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 16px;
        margin-top: 32px;
    }

    /* Chat Elements overrides */
    [data-testid="stChatMessage"] {
        border-radius: 16px;
        padding: 16px 20px;
        background: white;
        border: 1px solid #f1f5f9;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.02);
        margin-bottom: 16px;
    }

    /* Disclaimer */
    .disclaimer {
        background: linear-gradient(135deg, #fffbeb, #fef3c7);
        border: 1px solid #fde68a;
        color: #92400e;
        padding: 16px 20px;
        border-radius: 16px;
        font-size: 14px;
        margin-top: 40px;
        display: flex;
        align-items: flex-start;
        gap: 12px;
    }
    
    .disclaimer-icon {
        font-size: 20px;
    }

    .footer {
        text-align: center;
        color: #cbd5e1;
        font-size: 13px;
        margin-top: 32px;
        padding-bottom: 24px;
        font-weight: 500;
    }

    /* Sidebar styles */
    [data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #f1f5f9;
    }
    
    .sidebar-title {
        font-size: 20px;
        font-weight: 700;
        color: #0f172a;
        margin-bottom: 20px;
        background: linear-gradient(135deg, #0ea5e9, #3b82f6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .sidebar-list {
        list-style-type: none;
        padding-left: 0;
        color: #475569;
        font-size: 14px;
        line-height: 2.2;
    }
    
    .sidebar-list li::before {
        content: "✨";
        margin-right: 8px;
        font-size: 12px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# SESSION STATE
# ============================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "assistant" not in st.session_state:
    st.session_state.assistant = HealthConnectAssistant()


# ============================================================
# LAYOUT CONTAINERS
# ============================================================

header_container = st.container()
welcome_container = st.empty()
chat_container = st.container()
footer_container = st.container()

# ============================================================
# HEADER
# ============================================================

with header_container:
    st.markdown(
        """
        <div class="main-header">
            <div class="main-header-text">
                <h1>✨ HealthConnect</h1>
                <p>Your intelligent healthcare companion</p>
            </div>
            <div class="status">
                <span class="status-dot"></span>
                Online
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown('<div class="sidebar-title">HealthConnect AI</div>', unsafe_allow_html=True)

    st.markdown(
        """
        <ul class="sidebar-list">
            <li>Clinic information</li>
            <li>Opening hours</li>
            <li>Clinic locations</li>
            <li>Appointment details</li>
            <li>Appointment cancellation</li>
            <li>Appointment rescheduling</li>
        </ul>
        """,
        unsafe_allow_html=True
    )

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button(
        "✨ New conversation",
        use_container_width=True,
    ):
        st.session_state.messages = []
        st.rerun()

    st.markdown("<br><br><br>", unsafe_allow_html=True)
    st.caption(
        "Powered by Advanced RAG & LLMs"
    )


# ============================================================
# WELCOME MESSAGE
# ============================================================

if not st.session_state.messages:

    with welcome_container.container():
        st.markdown(
            """
            <div class="welcome-card">
                <h3>How can I help you today? 👋</h3>
                <p>
                I'm your HealthConnect assistant. You can ask me about
                clinic information, opening hours, or manage your appointments directly.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown('<div class="suggested-title">Suggested questions</div>', unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:

            if st.button(
                "🕐 Opening hours",
                use_container_width=True,
            ):
                st.session_state.pending_question = (
                    "What time does HealthConnect Clinic open?"
                )
                st.rerun()

            if st.button(
                "📍 Clinic locations",
                use_container_width=True,
            ):
                st.session_state.pending_question = (
                    "Where is HealthConnect Clinic located?"
                )
                st.rerun()

        with col2:

            if st.button(
                "📅 Check appointment",
                use_container_width=True,
            ):
                st.session_state.pending_question = (
                    "Check appointment HC-1001"
                )
                st.rerun()

            if st.button(
                "🔄 Reschedule",
                use_container_width=True,
            ):
                st.session_state.pending_question = (
                    "How can I reschedule my appointment?"
                )
                st.rerun()
else:
    welcome_container.empty()


# ============================================================
# PENDING QUESTION
# ============================================================

pending_question = st.session_state.pop(
    "pending_question",
    None,
)


# ============================================================
# CHAT INPUT
# ============================================================

user_message = st.chat_input(
    "Ask anything about HealthConnect..."
)

if pending_question:
    user_message = pending_question


# ============================================================
# PROCESS MESSAGE & DISPLAY CHAT
# ============================================================

with chat_container:
    # 1. Show existing history
    for message in st.session_state.messages:
        with st.chat_message(
            message["role"],
            avatar="✨" if message["role"] == "assistant" else "👤",
        ):
            st.markdown(message["content"])

    # 2. Process new message
    if user_message:
        st.session_state.messages.append(
            {
                "role": "user",
                "content": user_message,
            }
        )

        with st.chat_message("user", avatar="👤"):
            st.markdown(user_message)

        with st.chat_message("assistant", avatar="✨"):
            with st.spinner("Thinking..."):
                try:
                    answer = st.session_state.assistant.answer(user_message)
                except Exception as error:
                    answer = (
                        "I'm sorry, something went wrong while "
                        "processing your request. Please contact "
                        "HealthConnect Clinic reception."
                    )
                    print(f"[UI ERROR] {type(error).__name__}: {error}")
                
                st.markdown(answer)

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": answer,
            }
        )


# ============================================================
# DISCLAIMER & FOOTER
# ============================================================

with footer_container:
    st.markdown(
        """
        <div class="disclaimer">
            <div class="disclaimer-icon">⚠️</div>
            <div>
                <strong>Important Medical Disclaimer</strong><br>
                This assistant provides general information and administrative support only. 
                It does not diagnose conditions, offer medical advice, or replace emergency services.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="footer">
            HealthConnect Healthcare Information Assistant &copy; 2026
        </div>
        """,
        unsafe_allow_html=True,
    )
