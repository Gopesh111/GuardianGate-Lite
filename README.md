# 🛡️ GuardianGate Lite | AI Infrastructure Control Plane

[![Live Demo](https://img.shields.io/badge/Live_Demo-Hugging_Face-FFD21E?style=for-the-badge&logo=huggingface)](https://huggingface.co/spaces/Gopesh21/GuardianGate-Control-Plane)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)]()
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=for-the-badge&logo=fastapi&logoColor=white)]()
[![Streamlit](https://img.shields.io/badge/Streamlit-1.32+-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)]()

GuardianGate Lite is a high-performance, edge-level AI Proxy and Control Plane designed to sit between users and upstream LLM providers (like Groq/OpenAI). It implements enterprise-grade guardrails including **Zero-Trust PII Sanitization, Semantic Caching (FinOps), and Chaos Engineering** to ensure secure, cost-effective, and resilient AI deployments.

---

## ✨ Enterprise Capabilities

* **🛡️ Edge PII Sanitization:** Implements a zero-trust regex-based scrubber that intercepts and masks sensitive data (e.g., PINs, SSNs) *before* the payload ever leaves the local network. 
* **⚡ Semantic Caching (FAISS + FastEmbed):** Reduces API costs and latency. Instead of exact string matching, it uses `384-dimensional` vector embeddings to understand the *meaning* of a prompt. If a similar question was asked before (configurable strictness threshold), it returns the cached response instantly, bypassing the LLM call.
* **🚦 Chaos Engineering & Resilience:** Built-in circuit breakers handle upstream rate limits, 401s, or total cluster failures gracefully. Includes a "Chaos Toggle" to simulate LLM outages and test fallback routing mechanisms.
* **💰 Real-Time FinOps Telemetry:** A global dashboard tracking API health, cache hit ratios, vector bank size, and cumulative dollars saved in real-time.
* **🌊 Asynchronous Streaming:** Uses Server-Sent Events (SSE) and generator functions to stream high-speed AI responses with zero UI blocking.

---

## 🏗️ System Architecture

The architecture mimics industry-standard API Gateways (like Cloudflare for AI):

1. **Frontend (Hugging Face Spaces):** A stateful Streamlit control plane for telemetry and request dispatching.
2. **Backend (Render.com):** A scalable FastAPI ASGI server handling async request queues.
3. **Vector Engine (Local):** `qdrant/fastembed` generates lightweight embeddings on CPU, stored in a persistent `FAISS` index for millisecond retrievals.

---

## 🚀 Try it Live

The Control Plane is deployed and publicly accessible. Test the caching mechanism and PII scrubber here:
👉 **[GuardianGate Control Plane (Hugging Face)](https://huggingface.co/spaces/Gopesh21/GuardianGate-Control-Plane)**

*(Note: Try asking the same question twice in different words to see the Semantic Cache save API costs in real-time!)*

---

## 💻 Local Setup & Installation

Want to run the proxy server locally? Follow these steps:

### 1. Clone the repository
git clone https://github.com/Gopesh111/GuardianGate-Lite.git
cd GuardianGate-Lite

### 2. Set up a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

### 3. Install Dependencies
pip install -r requirements.txt

### 4. Configure Environment Variables
Create a `.env` file in the root directory and add your Groq API key:
GROQ_API_KEY=gsk_your_api_key_here

### 5. Start the Services
You need two terminal windows to run the microservices:

**Terminal 1 (FastAPI Backend):**
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

**Terminal 2 (Streamlit Control Plane):**
streamlit run app.py

---

## 🧪 Testing the Guardrails

1. **The Privacy Test:** Type `My secret pin is 1234. What is the capital of Japan?` -> Watch the event log scrub the PIN before the LLM sees it.
2. **The FinOps Test:** Ask `Who is the CEO of Google?`, then ask `Tell me who leads Google`. Watch the cache hit counter increment and bypass the API.
3. **The Chaos Test:** Toggle "Simulate LLM Failure" in the sidebar and watch the proxy gracefully return a System Guardrail error without crashing the main application thread.

---
*Built with modern Python async patterns for maximum throughput and reliability.*
