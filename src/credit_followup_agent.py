from __future__ import annotations

import csv
import os
import re
from datetime import UTC, date, datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INPUT_CSV = ROOT / "data" / "invoice_data_sample.csv"
OUTPUT_CSV = ROOT / "outputs" / "sample_emails_log.csv"


class Invoice:
    def __init__(self, row: dict[str, str]) -> None:
        self.invoice_no = require(row, "invoice_no")
        self.client_name = require(row, "client_name")
        self.client_email = require_email(row, "client_email")
        self.amount_due = require_positive_float(row, "amount_due")
        self.currency = require(row, "currency")
        self.due_date = date.fromisoformat(require(row, "due_date"))
        self.follow_up_count = int(row.get("follow_up_count") or 0)
        if self.follow_up_count < 0:
            raise ValueError("follow_up_count must be non-negative")
        self.last_sent_date = row.get("last_sent_date") or None
        self.payment_link = require(row, "payment_link")
        self.status = require(row, "status")


class EmailDraft:
    def __init__(self, subject: str, body: str, stage: int, tone: str) -> None:
        self.subject = subject
        self.body = body
        self.stage = stage
        self.tone = tone


def load_env_file(path: Path) -> None:
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


def require(row: dict[str, str], key: str) -> str:
    value = row.get(key, "").strip()
    if not value:
        raise ValueError(f"Missing required field: {key}")
    return value


def require_email(row: dict[str, str], key: str) -> str:
    value = require(row, key)
    if "@" not in value or "." not in value.rsplit("@", 1)[-1]:
        raise ValueError(f"Invalid email field: {key}")
    return value


def require_positive_float(row: dict[str, str], key: str) -> float:
    value = float(require(row, key))
    if value <= 0:
        raise ValueError(f"{key} must be positive")
    return value


def sanitize(value: str) -> str:
    cleaned = re.sub(r"<[^>]*>", "", str(value or ""))
    cleaned = re.sub(r"[`\"\\\\]", "", cleaned)
    return cleaned.strip()


def classify(invoice: Invoice, as_of: date) -> int | None:
    if invoice.status.strip().upper() in {"PAID", "LEGAL_REVIEW"}:
        return None
    if (invoice.last_sent_date or "").strip() == as_of.isoformat():
        return None
    days_overdue = (as_of - invoice.due_date).days
    if days_overdue <= 0:
        return None
    if invoice.follow_up_count >= 4 or days_overdue >= 30:
        return 5
    if days_overdue <= 7:
        return 1
    if days_overdue <= 14:
        return 2
    if days_overdue <= 21:
        return 3
    return 4


def render_email(invoice: Invoice, stage: int, days_overdue: int) -> EmailDraft:
    amount = f"{invoice.currency} {invoice.amount_due:,.0f}"
    common = (
        f"Invoice {invoice.invoice_no} for {amount} was due on "
        f"{invoice.due_date.isoformat()} and is now {days_overdue} days overdue.\n\n"
        f"Payment link: {invoice.payment_link}"
    )
    tones = {
        1: ("Warm and Friendly", "Friendly Reminder"),
        2: ("Polite but Firm", "Payment Pending"),
        3: ("Formal and Serious", "IMPORTANT: Outstanding Payment"),
        4: ("Stern and Urgent", "FINAL NOTICE"),
    }
    tone, prefix = tones[stage]
    if stage == 1:
        body = f"Hi {invoice.client_name},\n\nI hope you are well. This is a friendly reminder that {common}\n\nIf payment has already been processed, please ignore this note. Otherwise, kindly use the link above when convenient.\n\nRegards,\nFinance Team"
    elif stage == 2:
        body = f"Dear {invoice.client_name},\n\nThis is a polite follow-up on the pending payment. {common}\n\nPlease confirm the expected payment date or complete the payment using the link above.\n\nRegards,\nFinance Team"
    elif stage == 3:
        body = f"Dear {invoice.client_name},\n\nDespite prior reminders, this balance remains unpaid. {common}\n\nPlease respond within 48 hours with payment confirmation or a committed payment date so we can avoid disruption to credit terms.\n\nRegards,\nFinance Team"
    else:
        body = f"Dear {invoice.client_name},\n\nThis is the final automated notice for this overdue balance. {common}\n\nPlease arrange payment immediately. Continued non-payment may require escalation to finance and legal review.\n\nRegards,\nFinance Team"
    return EmailDraft(
        subject=f"{prefix} - {invoice.invoice_no} ({days_overdue} days overdue)",
        body=body,
        stage=stage,
        tone=tone,
    )


def load_invoices(path: Path) -> list[Invoice]:
    invoices: list[Invoice] = []
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            cleaned = {key: sanitize(value) for key, value in row.items()}
            try:
                invoices.append(Invoice(cleaned))
            except (ValueError, TypeError) as exc:
                raise SystemExit(f"Invalid invoice row {row.get('invoice_no')}: {exc}") from exc
    return invoices


def utc_now_iso() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")


def main() -> None:
    load_env_file(ROOT / ".env")
    as_of = date.fromisoformat(os.getenv("AS_OF_DATE", "2026-05-10"))
    dry_run = os.getenv("DRY_RUN", "true").lower() == "true"
    OUTPUT_CSV.parent.mkdir(exist_ok=True)

    rows: list[dict[str, str]] = []
    for invoice in load_invoices(INPUT_CSV):
        stage = classify(invoice, as_of)
        if stage is None:
            continue
        days_overdue = (as_of - invoice.due_date).days
        if stage == 5:
            rows.append(
                {
                    "timestamp": utc_now_iso(),
                    "invoice_no": invoice.invoice_no,
                    "client_name": invoice.client_name,
                    "client_email": invoice.client_email,
                    "amount_due": str(invoice.amount_due),
                    "days_overdue": str(days_overdue),
                    "stage": "5",
                    "tone_used": "Manual legal review",
                    "email_subject": "LEGAL_REVIEW_REQUIRED",
                    "send_status": "LEGAL_FLAGGED",
                    "dry_run": str(dry_run).lower(),
                }
            )
            continue
        draft = render_email(invoice, stage, days_overdue)
        rows.append(
            {
                "timestamp": utc_now_iso(),
                "invoice_no": invoice.invoice_no,
                "client_name": invoice.client_name,
                "client_email": invoice.client_email,
                "amount_due": str(invoice.amount_due),
                "days_overdue": str(days_overdue),
                "stage": str(draft.stage),
                "tone_used": draft.tone,
                "email_subject": draft.subject,
                "send_status": "DRY_RUN" if dry_run else "READY_TO_SEND",
                "dry_run": str(dry_run).lower(),
            }
        )

    fieldnames = [
        "timestamp",
        "invoice_no",
        "client_name",
        "client_email",
        "amount_due",
        "days_overdue",
        "stage",
        "tone_used",
        "email_subject",
        "send_status",
        "dry_run",
    ]
    with OUTPUT_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} audit/email rows to {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
