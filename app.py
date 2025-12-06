import streamlit as st
import requests
import json

# =========================
# n8n Webhook configuration
# =========================

N8N_WEBHOOK_URL = (
    "https://sudhakar-9000.app.n8n.cloud/webhook/cadf0c18-7c71-42cd-b878-894378064406"

)

# ==============#
# Streamlit page
# ==============

st.set_page_config(
    page_title="AI Translator (n8n + Gemini)",
    page_icon="🌐",
    layout="wide",
)

# ====================
# Custom Styling
# ====================

st.markdown(
    """
    <style>
    .main {
        padding-top: 2rem;
        background-color: #0f172a;
        color: #f9fafb;
    }
    .big-title {
        font-size: 2.4rem;
        font-weight: 700;
        margin-bottom: 0.3rem;
        color: #f9fafb;
    }
    .subtitle {
        font-size: 1rem;
        color: #9ca3af;
        margin-bottom: 1.5rem;
    }
    .translation-card {
        border-radius: 0.8rem;
        padding: 1rem 1.2rem;
        margin-bottom: 0.8rem;
        background-color: #1e293b;
        border: 1px solid #334155;
        box-shadow: 0 2px 6px rgba(0,0,0,0.3);
    }
    .translation-lang {
        font-weight: 600;
        font-size: 1rem;
        color: #a5b4fc;
        margin-bottom: 0.3rem;
    }
    .translation-text {
        font-size: 1.05rem;
        color: #f1f5f9;
        line-height: 1.5;
    }
    .stTextArea textarea {
        background-color: #1e293b !important;
        color: #f9fafb !important;
        border-radius: 0.5rem;
        border: 1px solid #334155;
    }
    .stButton>button {
        background-color: #6366f1;
        color: white;
        border-radius: 0.5rem;
        font-weight: 600;
        padding: 0.6rem 1.2rem;
        border: none;
        transition: 0.2s ease-in-out;
    }
    .stButton>button:hover {
        background-color: #4f46e5;
        transform: scale(1.02);
    }
    .footer {
        text-align: center;
        color: #9ca3af;
        font-size: 0.9rem;
        margin-top: 2rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ====================
# Header section
# ====================

st.markdown('<div class="big-title">🌐 AI Language Translator</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">Translate text instantly into multiple languages using your n8n + Gemini workflow. The app auto-detects the source language.</div>',
    unsafe_allow_html=True,
)

# ====================
# Layout
# ====================

col_left, col_right = st.columns([2, 1])

with col_left:
    text = st.text_area(
        "Text to translate",
        height=180,
        placeholder="Type or paste text in any language...",
    )

with col_right:
    st.write("Target languages")
    all_languages = [
        "English",
        "Hindi",
        "Telugu",
        "Tamil",
        "Kannada",
        "French",
        "Spanish",
        "German",
        "Japanese",
        "Chinese",
        "Arabic",
        "Russian",
    ]

    target_langs = st.multiselect(
        "Select one or more languages:",
        options=all_languages,
        default=["Hindi", "Telugu"],
    )

    st.caption("Source language is detected automatically by the model.")

# =========================
# Helper for reading n8n
# =========================

def extract_output_string(data):
    """
    Get the 'output' (or similar) string from n8n response.
    Expected shapes:
    1) [ { "json": { "output": "..." } } ]
    2) [ { "output": "..." } ]
    """
    if not isinstance(data, list) or not data:
        return None

    item = data[0]

    if isinstance(item, dict):
        inner = item.get("json", item)
    else:
        inner = {}

    for key in ["output", "translation", "text", "result"]:
        if isinstance(inner, dict) and key in inner:
            return inner[key]

    if isinstance(inner, str):
        return inner

    return None

# ====================
# Translate button
# ====================

st.markdown("---")

if st.button("🔁 Translate"):
    if not text.strip():
        st.warning("Please enter some text to translate.")
    elif not target_langs:
        st.warning("Please choose at least one target language.")
    else:
        try:
            with st.spinner("Contacting n8n..."):
                payload = {"text": text, "targetLangs": target_langs}
                response = requests.post(N8N_WEBHOOK_URL, json=payload, timeout=40)
                response.raise_for_status()
                data = response.json()

            raw_output = extract_output_string(data)

            if raw_output is None:
                st.error("Could not read translation JSON from n8n.")
                st.text(str(data))
            else:
                # raw_output should be a JSON string like {"Hindi":"...","Telugu":"..."}
                try:
                    translations = json.loads(raw_output)
                except Exception:
                    st.error("Could not parse JSON from model output.")
                    st.text(raw_output)
                    translations = {}

                if translations:
                    st.subheader("Translations")
                    col_a, col_b = st.columns(2)
                    columns = [col_a, col_b]
                    idx = 0
                    for lang, translation in translations.items():
                        with columns[idx % 2]:
                            st.markdown(
                                f"""
                                <div class="translation-card">
                                    <div class="translation-lang">{lang}</div>
                                    <div class="translation-text">{translation}</div>
                                </div>
                                """,
                                unsafe_allow_html=True,
                            )
                        idx += 1
                else:
                    st.warning("No translations found in response.")

        except Exception as e:
            st.error("Failed to contact n8n.")
            st.code(str(e))

st.markdown(
    """
    ---
    <div class="footer">
        Built with ❤️ by <b>Sudhakar Damarasingi</b>.
    </div>
    """,
    unsafe_allow_html=True,
)
