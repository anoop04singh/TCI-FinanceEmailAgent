# Sample Email Bodies

## Stage 1

Subject: Friendly Reminder - INV-2026-001 (5 days overdue)

Hi Rajesh Kapoor,

I hope you are well. This is a friendly reminder that Invoice INV-2026-001 for INR 45,000 was due on 2026-05-05 and is now 5 days overdue.

Payment link: https://pay.example.com/INV-2026-001

If payment has already been processed, please ignore this note. Otherwise, kindly use the link above when convenient.

Regards,  
Finance Team

## Stage 3

Subject: IMPORTANT: Outstanding Payment - INV-2026-003 (18 days overdue)

Dear Mohit Sharma,

Despite prior reminders, this balance remains unpaid. Invoice INV-2026-003 for INR 75,500 was due on 2026-04-22 and is now 18 days overdue.

Payment link: https://pay.example.com/INV-2026-003

Please respond within 48 hours with payment confirmation or a committed payment date so we can avoid disruption to credit terms.

Regards,  
Finance Team

## Stage 5 Legal Review

Subject: LEGAL_REVIEW_REQUIRED

Invoice INV-2026-005 for Arjun Mehta is 35 days overdue and has already reached the follow-up cap. The workflow outputs stage `5`, writes `stage` and `days_overdue` back to `Invoice_Data`, flags the record as `LEGAL_REVIEW`, appends a legal audit row, alerts the finance manager, and sends no automated client email.
