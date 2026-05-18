"""Extractor agent — pulls structured customer details from an email."""

from __future__ import annotations

from email_agent.models import Email, ExtractedInfo, Urgency
from email_agent.tools.llm import get_client

EXTRACTOR_SYSTEM_PROMPT = """You are an information extraction specialist for a small business.
Given a customer email, extract the following structured details:

- **customer_name**: The full name of the person writing (infer from signature or greeting; use "Unknown" if unclear).
- **need**: A concise, one-sentence summary of what the customer wants or needs.
- **location**: Any city, region, or address the customer mentions. Empty string if none.
- **urgency**: One of "low", "medium", "high", "critical".
  - critical: immediate threat, legal issue, or safety concern
  - high: tight deadline (within 24h), escalating complaint
  - medium: standard request with some time sensitivity
  - low: general enquiry with no deadline
- **key_facts**: A list of bullet-point facts extracted from the email (at most 5).

Reply with a JSON object containing all fields above.  Do not wrap in markdown.
"""


def extract(email: Email) -> ExtractedInfo:
    """Extract structured information from an email.

    Parameters
    ----------
    email : Email
        The parsed incoming email.

    Returns
    -------
    ExtractedInfo
    """
    client = get_client()

    messages = [
        {"role": "system", "content": EXTRACTOR_SYSTEM_PROMPT},
        {
            "role": "user",
            "content": f"Subject: {email.subject}\nFrom: {email.from_address}\n\nBody:\n{email.body}",
        },
    ]

    result = client.chat(
        messages,
        temperature=0.1,
        max_tokens=512,
        response_format={"type": "json_object"},
    )

    raw_urgency = result.get("urgency", "medium")
    try:
        urgency = Urgency(raw_urgency)
    except ValueError:
        urgency = Urgency.MEDIUM

    return ExtractedInfo(
        customer_name=str(result.get("customer_name", "Unknown")),
        need=str(result.get("need", "")),
        location=str(result.get("location", "")),
        urgency=urgency,
        key_facts=list(result.get("key_facts", [])),
    )
