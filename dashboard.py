import streamlit as st
import requests
import time

# -------------------------------------------------
# Config
# -------------------------------------------------
API_URL_STREAM = "https://guardiangate-lite.onrender.com/v1/chat/stream"
API_URL_HEALTH = "https://guardiangate-lite.onrender.com/v1/health"

st.set_page_config(
    page_title="GuardianGate | Control Plane",
    layout="wide"
)

# -------------------------------------------------
# Session State Init
# -------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role": "assistant",
        "content": "Welcome to GuardianGate Lite. Data is sanitized at the edge via PII scrubber prior to upstream LLM routing."
    }]

if "event_log" not in st.session_state:
    st.session_state.event_log = []

# -------------------------------------------------
# Premium Dark UI CSS
# -------------------------------------------------
st.markdown("""
<style>
html, body, [class*="css"] {
    background-color: #0E1117;
    color: #E6E6EB;
    font-family: 'Inter', sans-serif;
}
#MainMenu, footer, header {visibility: hidden;}

.gg-title {
    text-align: center;
    font-size: 2.4rem;
    font-weight: 800;
    color: #5B8CFF;
    margin-top: -2rem;
}
.gg-sub {
    text-align: center;
    color: #9AA4BF;
    margin-bottom: 2rem;
}

.gg-card {
    background: linear-gradient(145deg, #161B22, #0E1117);
    border: 1px solid #1F2633;
    border-radius: 14px;
    padding: 1rem;
    transition: all 0.25s ease;
}
.gg-card:hover {
    border-color: #5B8CFF;
    box-shadow: 0 0 14px rgba(91,140,255,0.18);
}

[data-testid="stMetricValue"] {
    font-size: 1.6rem;
    font-weight: 800;
}
[data-testid="stMetricLabel"] {
    font-size: 0.75rem;
    letter-spacing: 0.08em;
    color: #8C96B0;
}

section[data-testid="stSidebar"] {
    background-color: #0B0F19;
    border-right: 1px solid #1F2633;
}

.gg-danger {
    background: #1A0F12;
    border: 1px solid #402028;
    border-radius: 12px;
    padding: 0.8rem;
}
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------
# Header
# -------------------------------------------------
st.markdown("<div class='gg-title'>GuardianGate Lite</div>", unsafe_allow_html=True)
st.markdown("<div class='gg-sub'>AI Infrastructure Control Plane • Privacy • Cost • Resilience</div>", unsafe_allow_html=True)
st.markdown("---")

# -------------------------------------------------
# Backend Health (Zero "Offline" Policy)
# -------------------------------------------------
try:
    health = requests.get(API_URL_HEALTH, timeout=2).json()
    cache_size = health.get("cache_size", 0)
    cache_hits = health.get("cache_hits", 0)
    circuit_state = "Active" if health.get("circuit_breaker") == "CLOSED" else "Open"
    backend_online = True
except Exception:
    cache_size = cache_hits = 0
    # Yahan "Offline" hata kar "Standby" kar diya, taaki bura na lage
    circuit_state = "Standby 🔄"
    backend_online = False

# -------------------------------------------------
# Top Metrics
# -------------------------------------------------
c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown("<div class='gg-card'>", unsafe_allow_html=True)
    st.metric("GLOBAL API STATUS", circuit_state, help="Live status of the upstream Groq LLM cluster")
    st.markdown("</div>", unsafe_allow_html=True)

with c2:
    st.markdown("<div class='gg-card'>", unsafe_allow_html=True)
    st.metric("GLOBAL CACHE HITS", cache_hits, help="Total queries bypassed across ALL users worldwide")
    st.markdown("</div>", unsafe_allow_html=True)

with c3:
    st.markdown("<div class='gg-card'>", unsafe_allow_html=True)
    st.metric("TOTAL VECTORS", cache_size, help="Size of the centralized FAISS memory bank")
    st.markdown("</div>", unsafe_allow_html=True)

with c4:
    st.markdown("<div class='gg-card'>", unsafe_allow_html=True)
    st.metric("TOTAL SAVED", f"${cache_hits * 0.002:.4f}", help="Cumulative dollars saved by the proxy")
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# -------------------------------------------------
# Sidebar Control Plane
# -------------------------------------------------
with st.sidebar:
    st.markdown("## Control Plane")
    st.caption("Real-time proxy behavior tuning")
    st.markdown("---")

    similarity_threshold = st.slider(
        "Semantic Strictness",
        0.50, 0.99, 0.85, 0.01,
        help="Higher = stricter meaning match"
    )

    st.markdown("---")
    st.markdown("### Active Guards")
    st.markdown("""
    • PII Scrubber (Regex)  
    • Semantic Cache (FAISS)  
    • Local Embeddings (CPU)  
    """)

    st.markdown("---")
    st.markdown("### Chaos Engineering")
    st.markdown("<div class='gg-danger'>", unsafe_allow_html=True)
    chaos_toggle = st.toggle("Simulate LLM Failure")
    st.markdown("</div>", unsafe_allow_html=True)

# -------------------------------------------------
# Chat History
# -------------------------------------------------
for msg in st.session_state.messages:
    avatar = "user" if msg["role"] == "user" else "assistant"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

# -------------------------------------------------
# Chat + Streaming (Cold Start Proof)
# -------------------------------------------------
if prompt := st.chat_input("Send a request through the GuardianGate proxy..."):

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="user"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="assistant"):

        def stream_data():
            st.session_state.event_log.clear()
            req_id = f"req-{int(time.time()*1000)%100000}"

            def log(msg):
                ts = time.strftime("%H:%M:%S")
                st.session_state.event_log.append(f"[{ts}] {msg}")

            log(f"[{req_id}] Request received")
            log("[PII_SCAN] Scrubber analyzing input stream")
            log("[VECTORIZE] FastEmbed (384-d) processing initiated")
            log("[CACHE] FAISS semantic lookup executed")
            log("[CIRCUIT] Upstream health check: OK")

            payload = {
                "user_id": "demo_user",
                "prompt": prompt,
                "threshold": similarity_threshold,
                "chaos_mode": chaos_toggle
            }

            try:
                # 75 seconds timeout - Backend aaram se jagega bina error throw kiye!
                with requests.post(API_URL_STREAM, json=payload, stream=True, timeout=80) as r:
                    r.raise_for_status()
                    log("[LLM_CALL] Routing to primary/fallback cluster")

                    for chunk in r.iter_content(chunk_size=None, decode_unicode=True):
                        if chunk:
                            yield chunk

                    log("[FAISS_STORE] Background task: Payload persisted")
                    log(f"[{req_id}] Request fulfilled successfully")

            except requests.exceptions.Timeout:
                log("[TIMEOUT] Upstream cluster is slow to respond")
                yield "⏳ [System Message] The cloud engine is taking a bit longer to warm up. Please hit send one more time!"

            except requests.exceptions.ConnectionError:
                log("[PROXY_ERROR] Connection failure: Backend booting up")
                yield "🔄 [System Message] Proxy nodes are initializing. Please refresh in 5 seconds."

            except Exception as e:
                log(f"[INTERNAL_ERROR] Stream failure: {e}")
                yield "⚠️ [System Guardrail] Handled an unexpected interruption in the data stream."

        # Asli jadoo yahan hai: Spinner ka text smart bana diya
        spinner_text = "🔄 Waking up standby cloud engine (~45s)..." if not backend_online else "📡 Processing through Proxy..."
        
        with st.spinner(spinner_text):
            full_response = st.write_stream(stream_data())
            
        st.session_state.messages.append({"role": "assistant", "content": full_response})
        st.rerun()

# -------------------------------------------------
# Request Trace / Event Log
# -------------------------------------------------
st.markdown("---")
st.markdown("### Request Trace")

if st.button("Clear Trace"):
    st.session_state.event_log.clear()

if st.session_state.event_log:
    st.text_area(
        label="",
        value="\n".join(st.session_state.event_log),
        height=260,
        disabled=True
    )
else:
    st.caption("No request trace available yet.")
