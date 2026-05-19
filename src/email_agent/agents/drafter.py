"""Drafter agent — generates a reply draft based on email classification and extracted info."""

from __future__ import annotations

from email_agent.models import (
    Classification,
    Email,
    ExtractedInfo,
    ReplyDraft,
)
from email_agent.tools.llm import get_client

DRAFTER_SYSTEM_PROMPT = """You are a professional customer-service writer for a small business.
Given a customer email and its classification, write a polite, helpful reply draft.

Guidelines:
- Match the customer's tone but stay professional.
- For **quote_enquiry**: thank them, ask for any missing details needed to prepare the quote, and give a timeline.
- For **complaint**: acknowledge their frustration, apologise sincerely, outline next steps, and offer a contact method.
- For **booking**: confirm availability, ask for preferred date/time, and list what you need to finalise.
- For **support**: provide clear troubleshooting steps or ask for diagnostic details.
- For **spam**: write "NO_REPLY" as the subject and "This email was classified as spam. No reply needed." as the body.
- Always include a human review disclaimer at the end: "[This reply was AI-generated and requires human review before sending.]"
- Keep the reply concise (2-4 paragraphs).

Return a JSON object with:
  - "subject": the reply subject line (prefixed with "Re: " unless spam)
  - "body": the full reply body
  - "tone": the detected tone (e.g. "empathetic", "professional", "friendly")
"""


def draft_reply(
    email: Email,
    classification: Classification,
    extracted: ExtractedInfo,
) -> ReplyDraft:
    """Generate a reply draft for a classified and extracted email.

    Parameters
    ----------
    email : Email
        The original incoming email.
    classification : Classification
        Classification result from the classifier agent.
    extracted : ExtractedInfo
        Extracted customer details from the extractor agent.

    Returns
    -------
    ReplyDraft
    """
    client = get_client()

    user_content = (
        f"Category: {classification.category.value} (confidence: {classification.confidence:.0%})\n"
        f"Customer name: {extracted.customer_name}\n"
        f"Customer need: {extracted.need}\n"
        f"Urgency: {extracted.urgency.value}\n"
        f"Key facts: {', '.join(extracted.key_facts) if extracted.key_facts else 'none'}\n\n"
        f"Original email — Subject: {email.subject}\nBody:\n{email.body}"
    )

    messages = [
        {"role": "system", "content": DRAFTER_SYSTEM_PROMPT},
        {"role": "user", "content": user_content},
    ]

    result = client.chat(
        messages,
        temperature=0.3,
        max_tokens=1024,
        response_format={"type": "json_object"},
    )

    return ReplyDraft(
        subject=str(result.get("subject", f"Re: {email.subject}")),
        body=str(result.get("body", "Thank you for your email. We will get back to you shortly.")),
        tone=str(result.get("tone", "professional")),
        requires_human_review=True,
    )
