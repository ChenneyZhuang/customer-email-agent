"""Classifier agent — categorises an incoming email."""

from __future__ import annotations

from email_agent.models import Category, Classification, Email
from email_agent.tools.llm import get_client

CLASSIFIER_SYSTEM_PROMPT = """You are an email triage classifier for a small business.
Given a customer email, classify it into exactly ONE of these categories:

- **quote_enquiry**: Customer is asking for a price quote, estimate, or cost breakdown.
- **complaint**: Customer is unhappy about a product, service, delay, or experience.
- **booking**: Customer wants to schedule, reserve, or confirm an appointment/service.
- **support**: Customer needs technical help, troubleshooting, or how-to guidance.
- **spam**: Unsolicited marketing, phishing attempts, or completely irrelevant content.

Reply with a JSON object containing:
  - "category": one of the values above
  - "confidence": a float between 0.0 and 1.0
  - "reasoning": a short sentence explaining your choice
"""


def classify(email: Email) -> Classification:
    """Classify a single customer email.

    Parameters
    ----------
    email : Email
        The parsed incoming email.

    Returns
    -------
    Classification
    """
    client = get_client()

    messages = [
        {"role": "system", "content": CLASSIFIER_SYSTEM_PROMPT},
        {
            "role": "user",
            "content": f"Subject: {email.subject}\n\nBody:\n{email.body}",
        },
    ]

    result = client.chat(
        messages,
        temperature=0.1,
        max_tokens=256,
        response_format={"type": "json_object"},
    )

    return Classification(
        category=Category(result.get("category", "support")),
        confidence=float(result.get("confidence", 0.5)),
        reasoning=str(result.get("reasoning", "")),
    )
