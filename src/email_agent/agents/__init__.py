"""Agent modules for the email triage pipeline."""

from email_agent.agents.classifier import classify
from email_agent.agents.drafter import draft_reply
from email_agent.agents.extractor import extract

__all__ = ["classify", "draft_reply", "extract"]
