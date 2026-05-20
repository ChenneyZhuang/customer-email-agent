# 📬 Customer Email Agent

> **AI-powered email triage for small businesses.**
> Classify, extract, draft — but **never auto-send**. Human-in-the-loop by design.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Status: Alpha](https://img.shields.io/badge/Status-Alpha-orange.svg)]()
[![CI](https://github.com/ChenneyZhuang/customer-email-agent/actions/workflows/ci.yml/badge.svg)](https://github.com/ChenneyZhuang/customer-email-agent/actions/workflows/ci.yml)

---

## ✨ What It Does

Customer Email Agent helps small businesses handle incoming customer emails at scale.
Instead of sifting through your inbox manually, let the agent do the first pass:

| Step | What Happens |
|------|-------------|
| **1. Classify** | Categorises the email (quote enquiry, complaint, booking, support, or spam) using LLM |
| **2. Extract** | Pulls out structured details: customer name, need, location, urgency, key facts |
| **3. Draft** | Generates a professional reply draft tailored to category and tone |
| **4. Export** | Writes everything to CSV / JSON for CRM, Google Sheets, or database |

**🧑‍⚖️ Human-in-the-loop** — replies are *drafted* but **never sent automatically**.
Every draft requires human review before it reaches your customer.

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11 or later
- A [DeepSeek API key](https://platform.deepseek.com/) (or any OpenAI-compatible endpoint)

### 1. Install

```bash
# From GitHub
pip install git+https://github.com/ChenneyZhuang/customer-email-agent.git

# Or from source
git clone https://github.com/ChenneyZhuang/customer-email-agent.git
cd customer-email-agent
pip install -e .
```

### 2. Configure

```bash
cp .env.example .env
# Edit .env and paste your DEEPSEEK_API_KEY
```

Or set it directly:

```bash
export DEEPSEEK_API_KEY="sk-..."
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
            └── llm.py                # DeepSeek API client (httpx)
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

### Agent Details

**Classifier** — Determines the email category with confidence score:
- `quote_enquiry` — customer asking for price/estimate
- `complaint` — unhappy about product/service
- `booking` — wants to schedule/reserve
- `support` — needs help/troubleshooting
- `spam` — unsolicited/irrelevant

**Extractor** — Pulls structured info from the email body:
- Customer name (inferred from signature/greeting)
- Primary need (one-sentence summary)
- Location (if mentioned)
- Urgency level (low/medium/high/critical)
- Key facts (up to 5 bullet points)

**Drafter** — Generates a category-specific reply:
- Quote enquiry → thanks + asks for missing details + timeline
- Complaint → acknowledges frustration + apologises + next steps
- Booking → confirms availability + asks for preferred date/time
- Support → provides troubleshooting steps or diagnostic questions
- Spam → `NO_REPLY` marker (no draft generated)

---

## 🔧 CLI Reference

### `email-agent run` — Process one email

```bash
email-agent run \
  --from "customer@example.com" \
  --subject "Subject line" \
  --body "Email body text" \
  --id "msg-001"                # Optional, defaults to "cli-input"
  --body-file email.txt         # Alternative: read body from file
  --json                        # Output raw JSON instead of rich display
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

## 🐍 Python API

```python
from email_agent.pipeline import run, export_csv, export_json
from email_agent.models import Email

email = Email(
    id="msg-001",
    from_address="customer@example.com",
    subject="Need a quote",
    body="Hi, can I get a quote for a website?",
)

result = run(email)

print(result.classification.category)  # quote_enquiry
print(result.extracted.customer_name)  # Customer Name
print(result.reply.body)               # Drafted reply

# Export to CRM
csv_path = export_csv(result, email)
json_path = export_json(result, email)
```

---

## 🧰 Configuration

All settings via environment variables (or `.env` file):

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DEEPSEEK_API_KEY` | **Yes** | — | Your DeepSeek API key |
| `DEEPSEEK_BASE_URL` | No | `https://api.deepseek.com/v1` | API endpoint (OpenAI-compatible) |
| `DEEPSEEK_MODEL` | No | `deepseek-chat` | Model name |
| `EMAIL_AGENT_OUTPUT_DIR` | No | `./output` | Directory for CSV/JSON exports |

---

## 🧪 Testing

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run linting
ruff check src/

# Type checking
mypy src/
```

---

## 🔌 Hermes Agent Integration

This project ships with a `SKILL.md` for [Hermes Agent](https://hermes-agent.nousresearch.com/):

```bash
hermes skills install customer-email-agent
```

The skill teaches Hermes how to classify emails, extract customer info, draft replies,
and export CRM data — using this exact package.

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

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push and open a Pull Request

---

## 📄 License

MIT © [Chenney Zhuang](https://github.com/ChenneyZhuang)

---

## ⚠️ Disclaimer

This tool generates AI-drafted email replies intended for **human review only**.
The authors assume no liability for any communication sent without proper human
oversight. Always review AI-generated content before sending to customers.
