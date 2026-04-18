
# Streamlit automatically refreshes the browser when you save this file
# ============================================================

import streamlit as st
import joblib
import pandas as pd
import re

# ============================================================
# PAGE SETUP
# ============================================================
st.set_page_config(
    page_title="MPESA Phishing Detector",
    page_icon="assets/logob.png",
    layout="wide"   # "wide" uses full browser width. try "centered" to see the difference
)


# ============================================================
# LOAD THE MODEL
# @st.cache_resource tells Streamlit: "load this ONCE, then remember it"
# Without this, it would reload the model every single time someone clicks a button (slow!)
# ============================================================
@st.cache_resource
def load_model():
    try:
        return joblib.load("model/phishing_model.pkl")
    except FileNotFoundError:
        return None


model = load_model()


# ============================================================
# SESSION STATE
# Streamlit reruns the entire script every time a button is clicked
# st.session_state is how you REMEMBER things between those reruns
# Think of it like a backpack - you put things in, they stay there
# ============================================================
if "history" not in st.session_state:
    st.session_state.history = []

if "total_checked" not in st.session_state:
    st.session_state.total_checked = 0

if "total_fraud" not in st.session_state:
    st.session_state.total_fraud = 0


# ============================================================
# HELPER FUNCTION: FIND SUSPICIOUS WORDS
# This scans the message for known fraud keywords
# re.findall() uses regex to search - think of it as a smarter "find in text"
# ============================================================
FRAUD_KEYWORDS = [
    "won", "winner", "winning", "congratulations", "congratulation",
    "claim", "prize", "promo", "promotion", "reward",
    "urgent", "urgently", "immediately", "now", "today", "midnight",
    "suspended", "suspension", "deactivated", "blocked", "locked",
    "send kes", "send mpesa", "send via mpesa",
    "reactivate", "verify", "verification", "confirm identity",
    "lucky draw", "selected", "chosen", "lucky number",
    "double your money", "guaranteed", "100%",
    "free money", "free prize", "free gift",
    "processing fee", "admin fee", "registration fee", "delivery fee",
    "activate your account", "secure your account", "haraka", "mara moja", "sasa hivi", "chap chap", "upesi", "dharura",
    "mwisho wa leo", "kabla ya saa fulani", "tuma pesa", "tuma kwa mpesa", "lipa", "malipo", "ada", "karo", "fee",

    "gharama", "deposit", "toa pesa", "umeshinda", "mshindi", "umechaguliwa", "bahati yako", "zawadi", "tuzo",
    "bonasi", "offer", "promo", "bure", "zawadi ya pesa", "akaunti yako", "imefungwa", "itafungwa", "imesimamishwa",

    "thibitisha", "hakiki", "verify", "rejesha akaunti", "fungua akaunti", "piga simu", "wasiliana", "huduma kwa wateja",
    "agent", "afisa", "support", "msaada", "umetokea", "umeiva", "uko lucky", "fanya rada", "tuma haraka", "deal iko",
    "ni legit", "hakuna noma", "cash out", "chukua hii chance", "mshindi"


]


def find_suspicious_words(message):
    message_lower = message.lower()
    found = []
    for keyword in FRAUD_KEYWORDS:
        if keyword in message_lower:
            found.append(keyword)
    return found


# ============================================================
# SIDEBAR
# st.sidebar.anything() puts that element in the left panel
# ============================================================
with st.sidebar:
    st.title("📊 Dashboard")
    st.markdown("---")

    st.caption("**Session Summary**")

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Checked", st.session_state.total_checked)
    with col2:
        st.metric("Scams Blocked", st.session_state.total_fraud)

    # Calculate fraud rate
    if st.session_state.total_checked > 0:
        fraud_rate = (st.session_state.total_fraud /
                      st.session_state.total_checked) * 100
        st.metric("Fraud Rate", f"{fraud_rate:.0f}%")

    st.markdown("---")
    st.caption("🔑 Common Scam Words")

    keyword_html = ""
    for kw in ["won", "claim", "urgent", "send KES", "prize", "suspended", "verify", "fee"]:
        keyword_html += f'<span style="background:#ffe0e0;color:#d84848;padding:4px 10px;border-radius:12px;font-size:12px;margin:3px;display:inline-block;font-weight:500">{kw}</span>'
    st.markdown(keyword_html, unsafe_allow_html=True)

    st.markdown("---")
    st.caption("📱 **Built for Kenya**")
    st.markdown("""
    ✅ Understands Swahili & Sheng  
    ✅ Detects local scam patterns  
    ✅ 100% free & private  
    """)

    st.divider()
    st.caption("**🚨 Report Scams**")
    st.markdown("""
    📞 **Safaricom:** 0722 000 100  
    📞 **DCI Cyber:** 0800 722 724  
    """)


# ============================================================
# MAIN CONTENT
# ============================================================
col_brand, col_title = st.columns([0.2, 0.8])
with col_brand:
    st.image("assets/logob.png", width=220)
with col_title:
    st.markdown("# PhishGuard KE")
    st.markdown(
        "**🇰🇪 Detect M-PESA scams instantly** • Understands Swahili, Sheng & Local scam patterns")

st.markdown("---")
st.markdown("Paste an SMS below. We'll tell you if it's a scam.")

st.info("💡 This tool is built for Kenyans. It understands M-PESA scams, local language, and real attack patterns.")

if model is None:
    st.error("Model not found! Please run `python train_model.py` first.")
    st.stop()  # st.stop() stops the rest of the script from running


# ============================================================
# SAMPLE MESSAGES
# st.columns() splits the page into side-by-side columns
# Here we make 4 equal columns for 4 buttons
# ============================================================
st.subheader("📋 Try a sample message")
col1, col2, col3, col4 = st.columns(4)

SAMPLES = {
    "Legit payment":   "Confirmed. KES 1500 sent to Jane Wanjiku 0712XXXXXX on 14/4/26 at 10:23 AM. New M-PESA balance is KES 3240.00.",
    "Prize scam":      "Wewe ni mshindi wa 20GB data! Ili kuredeem, share ile code imeingia kwa SMS yako sasa hivi",
    "Account threat":  "URGENT: Your M-PESA account will be SUSPENDED. Send KES 100 to 0745XXXXXX to reactivate immediately.",
    "Doubling scam":   "MAMA PESA: Send KES 500 to 0722XXXXXX and receive KES 1000 back in 30 minutes. 100% Guaranteed!",
}

if col1.button("✅ Legit payment", width='stretch'):
    st.session_state.sample_text = SAMPLES["Legit payment"]

if col2.button("🎁 Prize scam", width='stretch'):
    st.session_state.sample_text = SAMPLES["Prize scam"]

if col3.button("⚠️ Account threat", width='stretch'):
    st.session_state.sample_text = SAMPLES["Account threat"]

if col4.button("💰 Doubling scam", width='stretch'):
    st.session_state.sample_text = SAMPLES["Doubling scam"]

st.markdown("---")


# ============================================================
# MESSAGE INPUT
# st.text_area() creates a multi-line text box
# value= sets what's pre-filled (empty string if no sample selected)
# ============================================================
st.subheader("✍️ Paste your message")
message = st.text_area(
    label="SMS message",
    value=st.session_state.get("sample_text", ""),
    height=120,
    placeholder="Paste MPESA message here...",
    label_visibility="collapsed"
)

st.caption(f"{len(message)} characters")

analyse_button = st.button(
    "Analyse message", type="primary", width="stretch")


# ============================================================
# ANALYSIS - runs when button is clicked AND there's a message
# ============================================================
if analyse_button and message.strip():

    prediction = model.predict([message])[0]
    probabilities = model.predict_proba([message])[0]
    fraud_confidence = probabilities[1] * 100
    legit_confidence = probabilities[0] * 100

    suspicious_words = find_suspicious_words(message)

    st.session_state.total_checked += 1
    if prediction == 1:
        st.session_state.total_fraud += 1

    st.session_state.history.append({
        "message": message[:60] + "..." if len(message) > 60 else message,
        "result":  "Phishing" if prediction == 1 else "Legit",
        "confidence": f"{fraud_confidence:.0f}%" if prediction == 1 else f"{legit_confidence:.0f}%"
    })

    st.markdown("---")

    def get_risk_level(confidence):
        if confidence >= 80:
            return "🔴 HIGH RISK", confidence
        elif confidence >= 60:
            return "🟡 MEDIUM RISK", confidence
        else:
            return "🟢 SAFE", confidence

    if prediction == 1:
        # FRAUD DETECTED
        risk_label, conf = get_risk_level(fraud_confidence)

        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #3d1414 0%, #2a0e0e 100%); border-left: 8px solid #d84848; padding: 30px; border-radius: 8px; margin: 30px 0;">
            <div style="text-align: center;">
                <h1 style="color: #ff6b6b; margin: 0; font-size: 48px;">⚠️ SCAM DETECTED</h1>
                <p style="color: #e0e0e0; font-size: 18px; margin-top: 10px;">High confidence this is a phishing attempt</p>
                <div style="margin-top: 20px;">
                    <span style="background-color: #d84848; color: white; padding: 12px 24px; border-radius: 8px; font-size: 20px; font-weight: bold; display: inline-block;">{conf:.0f}% Confidence</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        col_msg, col_analysis = st.columns([1, 1.2])

        with col_msg:
            st.markdown("**📌 Your Message:**")
            st.info(message)

        with col_analysis:
            st.markdown("**🔍 Why it's flagged as phishing:")
            if suspicious_words:
                for word in suspicious_words[:5]:
                    st.markdown(
                        f"- Contains **'{word}'** — common scam language")
            else:
                st.markdown("- Unusual patterns matching known scams")

        st.divider()

        col_do, col_dont = st.columns(2)
        with col_do:
            st.markdown("✅ **What to do:**")
            st.markdown("""
- Delete the message immediately
- Report to Safaricom: **0722 000 100**
- Alert your contacts about this number
            """)

        with col_dont:
            st.markdown("❌ **What NOT to do:**")
            st.markdown("""
- Don't send money
- Don't click links
- Don't call back
- Don't share OTP codes
            """)

    else:
        # LOOKS LEGIT
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #1a3d2a 0%, #0f2818 100%); border-left: 8px solid #51cf66; padding: 30px; border-radius: 8px; margin: 30px 0;">
            <div style="text-align: center;">
                <h1 style="color: #69db7c; margin: 0; font-size: 48px;">✅ SAFE MESSAGE</h1>
                <p style="color: #e0e0e0; font-size: 18px; margin-top: 10px;">Appears to be a genuine M-PESA transaction</p>
                <div style="margin-top: 20px;">
                    <span style="background-color: #51cf66; color: #0f2818; padding: 12px 24px; border-radius: 8px; font-size: 20px; font-weight: bold; display: inline-block;">{legit_confidence:.0f}% Confidence</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        col_msg, col_analysis = st.columns([1, 1.2])

        with col_msg:
            st.markdown("**📌 Your Message:**")
            st.success(message)

        with col_analysis:
            st.markdown("**✨ Why it looks legitimate:**")
            st.markdown("""
- Matches standard M-PESA format
- No urgency or pressure language
- Clear transaction details
            """)
            if not suspicious_words:
                st.markdown("- No known scam keywords detected")

elif analyse_button and not message.strip():
    # Button was clicked but no message was entered
    st.warning("Please paste a message first.")


# ============================================================
# HISTORY TABLE
# Shows the last 10 messages checked in this session
# ============================================================
if st.session_state.history:
    st.markdown("---")
    st.subheader("📊 Recent checks this session")

    # Convert the history list to a DataFrame for display
    history_df = pd.DataFrame(st.session_state.history)

    def color_result(val):
        if val == "Phishing":
            return "background-color: #3d1414; color: #ff6b6b; font-weight: bold"
        else:
            return "background-color: #1a3d2a; color: #69db7c; font-weight: bold"

    styled_df = history_df.style.map(color_result, subset=["result"])

    st.dataframe(
        styled_df,
        column_config={
            "message":    st.column_config.TextColumn("Message", width="large"),
            "result":     st.column_config.TextColumn("Result"),
            "confidence": st.column_config.TextColumn("Confidence"),
        },
        hide_index=True,
        use_container_width=True
    )

    if st.button("Clear history"):
        st.session_state.history = []
        st.session_state.total_checked = 0
        st.session_state.total_fraud = 0
        st.rerun()


# ============================================================
# FOOTER
# ============================================================
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #888; padding: 20px 0;">
    <p><strong>PhishGuard KE</strong> • Protecting Kenyans from M-PESA fraud</p>
    <p style="font-size: 12px;">Safaricom Report: 0722 000 100 | Cyber Crime Hotline: 0800 722 724</p>
    <p style="font-size: 11px;">Built with ML • Always free to use • Your messages stay private</p>
</div>
""", unsafe_allow_html=True)
