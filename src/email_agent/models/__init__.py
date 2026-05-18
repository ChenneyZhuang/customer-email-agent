"""Pydantic models for the email triage domain."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


# ── Enums ────────────────────────────────────────────────────────────────────


class Category(str, Enum):
    """Classification label for incoming customer emails."""

    QUOTE_ENQUIRY = "quote_enquiry"
    COMPLAINT = "complaint"
    BOOKING = "booking"
    SUPPORT = "support"
    SPAM = "spam"


class Urgency(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


# ── Input ────────────────────────────────────────────────────────────────────


class Email(BaseModel):
    """Raw email received from a customer."""

    id: str = Field(description="Unique identifier for the email (Message-ID or similar)")
    from_address: str = Field(alias="from", description="Sender email address")
    subject: str = Field(default="", description="Email subject line")
    body: str = Field(default="", description="Plain-text email body")
    received_at: Optional[datetime] = Field(default=None, description="When the email was received")


# ── Agent Outputs ────────────────────────────────────────────────────────────


class Classification(BaseModel):
    """Classification result from the classifier agent."""

    category: Category = Field(description="Predicted email category")
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence score")
    reasoning: str = Field(default="", description="Brief reasoning for the classification")


class ExtractedInfo(BaseModel):
    """Structured customer details extracted from the email body."""

    customer_name: str = Field(default="Unknown", description="Customer's full name")
    need: str = Field(default="", description="What the customer wants or is asking about")
    location: str = Field(default="", description="Customer location if mentioned")
    urgency: Urgency = Field(default=Urgency.MEDIUM, description="Perceived urgency")
    key_facts: list[str] = Field(default_factory=list, description="Bullet-point facts extracted from email")


class ReplyDraft(BaseModel):
    """AI-drafted reply — reviewed by a human before sending."""

    subject: str = Field(description="Reply subject line")
    body: str = Field(description="Full reply body text")
    tone: str = Field(default="professional", description="Detected or chosen tone")
    requires_human_review: bool = Field(default=True, description="Always True: human-in-the-loop enforced")


# ── Aggregated Result ────────────────────────────────────────────────────────


class TriageResult(BaseModel):
    """Complete triage output combining all agent results."""

    email_id: str
    classification: Classification
    extracted: ExtractedInfo
    reply: ReplyDraft
    processed_at: datetime = Field(default_factory=datetime.utcnow)


# ── CRM Export ───────────────────────────────────────────────────────────────


class CRMRecord(BaseModel):
    """Flat record for CRM / CSV / Google Sheets export."""

    email_id: str
    from_address: str
    subject: str
    received_at: str
    category: str
    confidence: float
    customer_name: str
    need: str
    location: str
    urgency: str
    reply_subject: str
    reply_body: str
    processed_at: str

    @classmethod
    def from_triage(cls, result: TriageResult, email: Email) -> CRMRecord:
        """Create a CRMRecord from a TriageResult and the original Email."""
        return cls(
            email_id=result.email_id,
            from_address=email.from_address,
            subject=email.subject,
            received_at=email.received_at.isoformat() if email.received_at else "",
            category=result.classification.category.value,
            confidence=result.classification.confidence,
            customer_name=result.extracted.customer_name,
            need=result.extracted.need,
            location=result.extracted.location,
            urgency=result.extracted.urgency.value,
            reply_subject=result.reply.subject,
            reply_body=result.reply.body,
            processed_at=result.processed_at.isoformat(),
        )
