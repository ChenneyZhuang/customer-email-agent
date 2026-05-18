# SKILL: customer-email-agent

## Overview

Customer Email Agent is an AI-powered email triage tool for small businesses. It
classifies incoming customer emails, extracts structured details, drafts replies,
and exports CRM-ready data — with **human-in-the-loop** enforcement (never
auto-sends).

## Installation

```bash
git clone https://github.com/ChenneyZhuang/customer-email-agent.git
cd customer-email-agent
pip install -e .
cp .env.example .env
# Edit .env with your DEEPSEEK_API_KEY
```

## When to Use

- User asks to triage, classify, or draft replies for customer emails
- User wants to extract structured data from email text
- User needs CRM-ready CSV/JSON exports from email content
- User mentions "email agent", "customer email triage", or similar

## Usage

### CLI (recommended for one-off emails)

```bash
email-agent run --from "sender@example.com" --subject "Subject" --body "Body text"
email-agent run --from "sender@example.com" --body-file email.txt
email-agent batch emails.csv
```

### Python API

```python
from email_agent.models import Email
from email_agent.pipeline import run, export_csv, export_json

email = Email(id="msg-1", from_="alice@ex.com", subject="Quote", body="...")
result = run(email)
csv_path = export_csv(result, email)
json_path = export_json(result, email)

print(result.classification.category)    # Category enum
print(result.extracted.customer_name)    # str
print(result.reply.body)                 # draft reply
```

## Key Design Principles

1. **Human-in-the-loop**: `reply.requires_human_review` is always `True`. Never send AI drafts directly.
2. **Structured I/O**: All inputs and outputs use Pydantic models for type safety.
3. **Modular agents**: classifier, extractor, and drafter are independent — swap or extend any.
4. **CRM-ready exports**: CSV format maps directly to Google Sheets / CRM imports.

## Environment Variables

- `DEEPSEEK_API_KEY` (required) — API key for DeepSeek
- `DEEPSEEK_BASE_URL` — override for OpenAI-compatible proxies
- `DEEPSEEK_MODEL` — model name (default: `deepseek-chat`)
- `EMAIL_AGENT_OUTPUT_DIR` — export directory (default: `./output`)

## Repository

https://github.com/ChenneyZhuang/customer-email-agent
