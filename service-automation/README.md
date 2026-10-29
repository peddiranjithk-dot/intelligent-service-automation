# Intelligent Service Automation

A simple base project: employees submit service requests; the system **classifies** them
(TF-IDF + Logistic Regression), **prioritises** (urgency keywords), **routes** to the right team,
sets an **SLA**, and **auto-resolves** common requests (password reset, VPN) from a knowledge base.

## Run
    pip install -r requirements.txt
    python app.py          # http://localhost:5000
    pytest -q              # run tests

## API
| Method | Endpoint | Purpose |
|---|---|---|
| POST | /api/requests | `{requester,title,description}` -> triaged request |
| GET | /api/requests?status=assigned | list, sorted by priority |
| PATCH | /api/requests/<id> | `{status}` |
| GET | /api/stats | totals, automation rate, breakdowns |

## Files
- `training_data.py` - seed examples per intent (add rows to improve the model)
- `automation.py` - classifier, priority, routing, auto-resolution, knowledge base
- `app.py` - Flask API + SQLite; `templates/index.html` - small UI

## Extend
Replace the classifier with an LLM call, add email/Slack notifications, auth, and real ITSM integration (ServiceNow/Jira).
