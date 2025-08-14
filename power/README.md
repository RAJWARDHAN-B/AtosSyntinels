# Power Platform Solution

This folder will host the exported Power Apps solution and Power Automate flows.

Apps:
- Reviewer Workspace (Canvas app)
- Configuration Center (model-driven or canvas)

Flows:
- Approvals and SLA notifications (Teams/Outlook)
- Document status updates and export to SharePoint/OneDrive

## Local UI (Zero-Cost Alternative)
If you need a free/local UI instead of Power Apps/Automate, plan for a small Streamlit app and lightweight automations:

- Streamlit reviewer workspace (upload, view clauses, risk, summaries)
- Python background tasks (Celery/RQ) or simple FastAPI endpoints for async processing
- Notifications via local email (SMTP) simulator or console logs

See `local/` for the underlying services.