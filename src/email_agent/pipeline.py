"""End-to-end email triage pipeline.

Orchestrates: classify → extract → draft → export.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

from email_agent import config
from email_agent.agents import classify, draft_reply, extract
from email_agent.models import CRMRecord, Email, TriageResult


def run(email: Email) -> TriageResult:
    """Execute the full triage pipeline on a single email.

    Parameters
    ----------
    email : Email
        The parsed incoming email.

    Returns
    -------
    TriageResult
        Complete triage result containing classification, extraction, and draft.
    """
    classification = classify(email)
    extracted = extract(email)
    reply = draft_reply(email, classification, extracted)

    result = TriageResult(
        email_id=email.id,
        classification=classification,
        extracted=extracted,
        reply=reply,
    )
    return result


def export_csv(result: TriageResult, email: Email, output_path: Path | None = None) -> Path:
    """Export a triage result to CSV (CRM-ready format).

    Appends to the file if it already exists, writes a header otherwise.

    Parameters
    ----------
    result : TriageResult
        The completed triage result.
    email : Email
        The original email (needed for fields not in TriageResult).
    output_path : Path or None
        Destination file path. Defaults to ``config.OUTPUT_DIR / "crm_export.csv"``.

    Returns
    -------
    Path
        The path to the CSV file.
    """
    if output_path is None:
        output_path = config.OUTPUT_DIR / "crm_export.csv"
    else:
        output_path = Path(output_path)

    record = CRMRecord.from_triage(result, email)
    file_exists = output_path.exists()

    with open(output_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(CRMRecord.model_fields.keys()))
        if not file_exists:
            writer.writeheader()
        writer.writerow(record.model_dump())

    return output_path


def export_json(result: TriageResult, email: Email, output_path: Path | None = None) -> Path:
    """Export a full triage result to a pretty-printed JSON file.

    Parameters
    ----------
    result : TriageResult
        The completed triage result.
    email : Email
        Original email (included for completeness).
    output_path : Path or None
        Destination file path. Defaults to
        ``config.OUTPUT_DIR / "{email_id}_triage.json"``.

    Returns
    -------
    Path
        The path to the JSON file.
    """
    if output_path is None:
        output_path = config.OUTPUT_DIR / f"{email.id}_triage.json"
    else:
        output_path = Path(output_path)

    data = {
        "email": email.model_dump(mode="json"),
        "triage": result.model_dump(mode="json"),
    }

    output_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path
