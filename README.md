# 📬 Customer Email Agent

> **AI-powered email triage for small businesses.**
> Classify, extract, draft — but **never auto-send**. Human-in-the-loop by design.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

---

## ✨ What It Does

Customer Email Agent is an open-source AI agent that helps small businesses handle
incoming customer emails at scale. Instead of sifting through your inbox manually,
let the agent do the first pass:

| Step | What Happens |
|------|-------------|
| **1. Classify** | Categorises the email (quote enquiry, complaint, booking, support, or spam) using LLM inference |
| **2. Extract** | Pulls out structured details: customer name, need, location, urgency, key facts |
| **3. Draft** | Generates a professional reply draft tailored to the category and tone |
| **4. Export** | Writes everything to CSV / JSON for your CRM, Google Sheets, or database |

**🧑‍⚖️ Human-in-the-loop** — replies are *drafted* but **never sent automatically**.
Every draft requires human review before it reaches your customer.

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11 or later
- A [DeepSeek API key](https://platform.deepseek.com/) (or any OpenAI-compatible endpoint)

### 1. Install

```bash
pip install -e .
```

Or from PyPI (coming soon):

```bash
pip install email-agent
```

### 2. Configure

```bash
cp .env.example .env
# Edit .env and paste your DEEPSEEK_API_KEY
```

### 3. Run

```bash
email-agent run \
  --from "alice@example.com" \
  --subject "Need a quote for wedding cake" \
  --body "Hi, I'm getting married on June 15th and need a 3-tier cake for 80 guests. Can you send me a quote? I'm in Austin, TX. — Alice"
```

**Output:**

```
╭────────────────── 📬 Email Triage Result ──────────────────╮
│ Classification: quote_enquiry (95% confidence)             │
│ Customer is asking for a price quote for a wedding cake.   │
╰────────────────────────────────────────────────────────────╯

              📋 Extracted Details
┌──────────────┬──────────────────────────────────┐
│ Customer     │ Alice                            │
│ Need         │ Price quote for 3-tier wedding … │
│ Location     │ Austin, TX                       │
│ Urgency      │ high                             │
│ Key Facts    │ • Wedding date: June 15th        │
│              │ • 80 guests                      │
│              │ • 3-tier cake                    │
└──────────────┴──────────────────────────────────┘

╭── ✉️  Re: Need a quote for wedding cake ───────────────────╮
│ Dear Alice,                                                 │
│                                                             │
│ Thank you for reaching out and congratulations on your      │
│ upcoming wedding! I'd love to prepare a quote for your      │
│ 3-tier cake for 80 guests. …                                │
│                                            Tone: friendly   │
│                              Requires human review          │
╰────────────────────────────────────────────────────────────╯

CSV exported → ./output/crm_export.csv
JSON exported → ./output/cli-input_triage.json
```

---

## 📦 Package Structure

```
customer-email-agent/
├── README.md
├── LICENSE
├── pyproject.toml
├── .env.example
├── .gitignore
├── SKILL.md                          # Hermes Agent skill definition
└── src/
    └── email_agent/
        ├── __init__.py               # Package metadata
        ├── cli.py                    # Typer CLI (run, batch, version)
        ├── pipeline.py               # Orchestrator & CSV/JSON export
        ├── config.py                 # Env-based configuration
        ├── models/
        │   ├── __init__.py           # Pydantic domain models
        │   └── schemas.py            # Re-exports
        ├── agents/
        │   ├── __init__.py           # Agent re-exports
        │   ├── classifier.py         # Email categorisation
        │   ├── extractor.py          # Customer info extraction
        │   └── drafter.py            # Reply draft generation
        └── tools/
            └── llm.py                # DeepSeek API client
```

---

## 🧩 Architecture

```
┌──────────┐     ┌──────────────┐     ┌──────────────┐     ┌───────────┐
│  Email   │────▶│  Classifier  │────▶│  Extractor   │────▶│  Drafter  │
│  (input) │     │  Agent       │     │  Agent       │     │  Agent    │
└──────────┘     └──────────────┘     └──────────────┘     └───────────┘
                       │                     │                    │
                       ▼                     ▼                    ▼
                 Classification        ExtractedInfo         ReplyDraft
                       │                     │                    │
                       └─────────────────────┴────────────────────┘
                                             │
                                       ┌─────▼─────┐
                                       │  Pipeline │
                                       │  Export   │
                                       └─────┬─────┘
                                             │
                              ┌──────────────┴──────────────┐
                              ▼                             ▼
                         CSV (CRM)                      JSON
```

Each agent is an independent module that calls the LLM with a specialised system
prompt. Results flow through Pydantic models for type safety and serialisation.

---

## 🔧 CLI Reference

### `email-agent run` — Process one email

```bash
email-agent run \
  --from "customer@example.com" \
  --subject "Subject line" \
  --body "Email body text" \
  --id "msg-001"                # optional, defaults to "cli-input"
  --body-file email.txt         # alternative: read body from file
  --json                        # output raw JSON instead of rich display
```

### `email-agent batch` — Process a CSV of emails

```bash
email-agent batch emails.csv --output ./output/batch_result.csv
```

CSV format:

| id | from | subject | body |
|----|------|---------|------|
| msg-1 | alice@ex.com | Quote needed | Hi, I need a quote... |

### `email-agent --version`

Print version and exit.

---

## 🧰 Configuration

All settings via environment variables (or `.env` file):

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DEEPSEEK_API_KEY` | **Yes** | — | Your DeepSeek API key |
| `DEEPSEEK_BASE_URL` | No | `https://api.deepseek.com/v1` | API endpoint (supports OpenAI-compatible proxies) |
| `DEEPSEEK_MODEL` | No | `deepseek-chat` | Model name |
| `EMAIL_AGENT_OUTPUT_DIR` | No | `./output` | Directory for CSV/JSON exports |

---

## 🧪 Development

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Run linting
ruff check src/

# Type checking
mypy src/
```

---

## 🛣️ Roadmap

- [ ] FastAPI web interface with dashboard
- [ ] SQLite storage for triage history
- [ ] Google Sheets direct integration
- [ ] Multi-provider LLM support (OpenAI, Anthropic, local models)
- [ ] Email ingestion via IMAP / Gmail API
- [ ] Custom reply templates per category
- [ ] Confidence threshold for auto-archiving spam

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

MIT © [Chenney Zhuang](https://github.com/ChenneyZhuang)

---

## ⚠️ Disclaimer

This tool generates AI-drafted email replies intended for **human review only**.
The authors assume no liability for any communication sent without proper human
oversight. Always review AI-generated content before sending to customers.
