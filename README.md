# plugin-fact-checking

# 🇻🇳 Vietnamese FactCheck Plugin (ViFactCheck / VeriCheck)

A real-time **fact-checking browser plugin** for Vietnamese language claims, integrating **Natural Language Processing (NLP)** and **Large Language Models (LLMs)**.  
The plugin helps users verify online claims instantly while browsing, with clear evidence and confidence scoring.

---

## 🌐 Overview

**Vietnamese FactCheck Plugin** (VeriCheck) is a Chrome Extension linked to a backend fact-verification system.  
Users can type or highlight any Vietnamese claim (e.g., *"Jack bỏ con"*) and receive an instant result — showing whether the claim is **Supported**, **Refuted**, or **Not Enough Information**, along with confidence and evidence links.

<div align="center">
  <img src="system_overview.png" width="700" alt="System Architecture">
</div>

The system pipeline:
1. Reformulate user claim → **neutral search query (Gemini)**
2. **Google Search (Serper.dev)** → retrieve top results
3. Extract clean text via **Trafilatura**
4. Rank evidence using **BM25 + SBERT Hybrid**
5. Verify claim using **PhoBERT / XLM-R**
6. Summarize & rewrite claim using **Gemini LLM**

---

## 🧠 System Architecture

| Stage | Module | Description |
|-------|---------|-------------|
| **Frontend** | Chrome Extension | Collects claim, displays fact-check result |
| **Backend** | FastAPI + PyTorch | Handles query optimization, retrieval, verification |
| **Retrieval** | Gemini → Serper.dev → Trafilatura | Optimized query → web search → text extraction |
| **Reranking** | BM25 + SBERT Hybrid | Combines lexical & semantic similarity |
| **Verification** | PhoBERT / XLM-R | Predicts SUPPORT / REFUTE with confidence |
| **Rewrite** | Gemini LLM | Suggests corrected or neutral rephrasing |

---

## 🧩 Key Features

- ✅ Real-time fact-checking with live Vietnamese web data  
- 🌍 Optimized for Vietnamese syntax and news sources  
- 🔍 Hybrid retrieval (BM25 + SBERT)  
- 🤖 Transformer-based veracity prediction  
- 💬 Gemini explanations and corrected rewrites  
- 🔒 Source filtering (HTTPS + verified journalism)  
- 📊 Confidence visualization and evidence linking  

---

## 🖥️ Plugin Interface

<div align="center">
  <img src="plugin_support.png" width="350" alt="Plugin Interface Screenshot">
</div>

**Example:**
> **Input:** `jack bỏ con`  
> **Output:** ✅ Claim appears true (Confidence: 66.67%)  
> **Evidence:** from *tienphong.vn*  
> **Verdict:** SUPPORTS (2) | REFUTES (1)  
> **Action:** Suggests factual rephrasing for user clarity.

---

## ⚙️ Technical Details

- **Backend:** Python, FastAPI  
- **Libraries:** PyTorch, Trafilatura, Sentence-BERT  
- **Retrieval API:** [Serper.dev](https://serper.dev/)  
- **LLM Query Optimizer:** Gemini 2.0 Flash  
- **Models:** PhoBERT-base, XLM-R-Large  
- **Dataset:** [ViFactCheck (AAAI 2025)](https://arxiv.org/abs/2503.19786)

---

## 🧪 Experimental Results

### Claim Verification

| Model | Accuracy | F1-score |
|--------|-----------|----------|
| XLM-R-Large | 0.8590 | 0.8591 |
| PhoBERT-base *(Deployed)* | 0.8417 | 0.8422 |

### Evidence Selection

| Method | ACC@3 | mAP@3 | Latency (ms) |
|--------|--------|--------|---------------|
| BM25 | 0.44 | 0.44 | 1.97 |
| SBERT | 0.42 | 0.49 | 104.3 |
| **Hybrid (BM25 + SBERT)** | **0.57** | **0.52** | **20.2** |

---

## 📦 Installation

### 1. Clone repository
```bash
git clone https://github.com/<your-username>/Vietnamese-FactCheck-Plugin.git
cd Vietnamese-FactCheck-Plugin
