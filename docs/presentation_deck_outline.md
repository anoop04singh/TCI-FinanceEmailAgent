# Presentation Deck Outline

## Slide 1: Title

Finance Credit Follow-Up Email Agent  
Automated overdue invoice reminders with dry-run safety and audit logging.

## Slide 2: Problem

Finance teams manually chase overdue invoices, causing inconsistent tone, missed reminders, limited audit trails, and delayed legal escalation.

## Slide 3: Solution

n8n workflow that reads invoice data, skips already-processed records, classifies overdue accounts, batches Stage 1-4 invoices into Gemini chunks, sends or dry-runs emails, logs every action, updates stage tracking, and flags legal review cases.

## Slide 4: Architecture

Show the Mermaid flow from README:

Schedule Trigger -> Google Sheets -> Classify -> Stage 5 legal branch or Aggregate Batch -> Has Invoices -> Split Into Chunks -> AI Agent + Gemini + Structured Parser -> Validator -> Dry-run/SMTP -> Audit Log -> Invoice update.

## Slide 5: Stage Escalation

Stage 1: 1-7 days, warm reminder.  
Stage 2: 8-14 days, polite but firm.  
Stage 3: 15-21 days, formal with 48-hour response.  
Stage 4: 22-29 days, final notice.  
Stage 5: 30+ days or four follow-ups, human review.

## Slide 6: LLM and Framework Choices

Gemini 2.0 Flash for low-cost batch JSON email generation.  
n8n for visual orchestration, credential management, scheduling, Google Sheets, SMTP, structured parsing, chunking, and auditability.

## Slide 7: Security Controls

Prompt injection mitigation, slim AI payloads, `.env` and n8n credential vault, structured JSON validation, chunk-by-chunk invoice matching, dry-run mode, verified SMTP sender, today-filter, and legal/human review branch.

## Slide 8: Demo Results

Six sample invoices:

- Four generated dry-run email audit rows.
- One Stage 5 legal review flag.
- One paid invoice skipped.

## Slide 9: Learnings

Structured batch output reduced per-record AI overhead.  
Chunking made the workflow safer for larger invoice volumes.  
Dry-run mode and deterministic routing kept email sending controlled.

## Slide 10: Future Work

Langfuse or LangSmith tracing, dashboard metrics, manager approval queue for Stage 4, CRM integration, and payment-status reconciliation before sending.
