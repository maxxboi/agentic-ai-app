<div align="center">

# 📄 Resume Analyzer

**AI-powered resume parsing & job-description matching, built with LangChain + Groq**

Upload a resume, get clean structured data back, then match it against any job
description to get a score, matched/missing skills, strengths, and gaps —
all in seconds.

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/UI-Streamlit-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![LangChain](https://img.shields.io/badge/Framework-LangChain-1C3C3C)](https://www.langchain.com/)
[![Groq](https://img.shields.io/badge/LLM-Groq-orange)](https://groq.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](#license)

</div>

---

## ✨ Features

- **📤 Resume parsing** — upload a PDF resume and get structured data back: name, email, phone, skills, education, and work experience
- **🎯 JD matching** — paste any job description and get an instant fit assessment
- **📊 Match score** — a 0–100 score summarizing overall fit
- **✅ Matched & ❌ missing skills** — see exactly what aligns and what's missing
- **💪 Strengths & ⚠️ gaps** — a recruiter-style breakdown, not just keyword matching
- **🧾 Raw JSON view** — inspect the exact structured output for debugging or downstream use
- **⚡ Fast** — powered by Groq's LPU inference, responses in seconds

---

## 🖥️ Demo

| Upload & Parse | Match Against a JD |
|---|---|
| Upload a PDF resume from the sidebar and click **Parse Resume** | Paste a job description and click **Run JD Match** |

> Add your own screenshots here once you run the app locally — drop them in a
> `docs/` or `assets/` folder and reference them like:
> `![Parsed resume view](docs/screenshot-parse.png)`

---

## 🏗️ How it works

```
PDF Resume ──▶ pypdf (text extraction) ──▶ Groq LLM ──▶ structured Resume (Pydantic)
                                                              │
Job Description ─────────────────────────────────────────────┘
                                │
                          Groq LLM (matching)
                                │
                                ▼
                     MatchResult (score, skills, gaps, summary)
```

Both parsing and matching use **LangChain's structured output parsing**
(`PydanticOutputParser`) so the LLM's response is always validated into a
typed, predictable schema — no fragile regex or manual JSON wrangling.

---

## 📁 Project structure

```
resume-analyzer/
├── app.py              # Streamlit UI — upload, parse, and match
├── parser.py            # PDF text extraction + LLM resume parsing (Pydantic models: Resume, Education, Experience)
├── matcher.py            # LLM-based JD matching (Pydantic model: MatchResult)
├── requirements.txt      # Python dependencies
├── .env.example           # Template for your GROQ_API_KEY
└── uploads/                # Uploaded resumes are saved here (gitignored)
```

---

## 🚀 Getting started

### Prerequisites

- Python 3.10+
- A free [Groq API key](https://console.groq.com/keys)

### 1. Clone the repo

```bash
git clone https://github.com/<your-username>/resume-analyzer.git
cd resume-analyzer
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

> Tip: use a virtual environment
> `python -m venv venv && source venv/bin/activate` (Windows: `venv\Scripts\activate`)

### 3. Configure your API key

```bash
cp .env.example .env
```

Then edit `.env`:

```env
GROQ_API_KEY=gsk_your_key_here
```

### 4. Run the app

```bash
streamlit run app.py
```

Open **http://localhost:8501** in your browser.

---

## 🧑‍💻 Usage

1. **Upload a resume** — sidebar → choose a PDF → **Parse Resume**
2. **Review the extracted data** — candidate info, skills, education, and experience are displayed side by side (raw JSON is available in an expander)
3. **Paste a job description** — under *Match Against a Job Description*
4. **Run JD Match** — get a match score, matched/missing skills, strengths, gaps, and a summary

---

## ⚙️ Configuration

| Setting | Where | Default |
|---|---|---|
| LLM model | `parser.py` → `get_llm()` | `llama-3.3-70b-versatile` |
| Temperature | `parser.py` → `get_llm()` | `0.0` |
| Upload directory | `app.py` → `UPLOAD_DIR` | `uploads/` |

Swap the model to any other [Groq-hosted model](https://console.groq.com/docs/models) by changing the `model` argument in `get_llm()`.

---

## 🛠️ Tech stack

- [Streamlit](https://streamlit.io/) — UI
- [LangChain](https://www.langchain.com/) — prompting & structured output parsing
- [Groq](https://groq.com/) — LLM inference
- [pypdf](https://pypdf.readthedocs.io/) — PDF text extraction
- [Pydantic](https://docs.pydantic.dev/) — data validation & schemas

---

## 🗺️ Roadmap ideas

- [ ] Support DOCX resumes
- [ ] Batch-process multiple resumes against one JD
- [ ] Export match report as PDF
- [ ] OCR support for scanned resumes
- [ ] Resume improvement suggestions based on JD gaps

---

## 🤝 Contributing

Contributions are welcome! Feel free to open an issue or submit a PR:

1. Fork the repo
2. Create a branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -m "Add your feature"`)
4. Push and open a PR

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

---

<div align="center">

Built with ❤️ using LangChain and Groq

</div>
