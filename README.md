# Workplace Operations Dashboard

Streamlit demo for the MoveInSync Technical Account Manager / Implementation Intern seating-capacity assessment.

## Features
- Editable headcount, office days, working days, planning buffer and office split
- Theoretical minimum, illustrative starting capacity and maximum simultaneous seats
- Office-level estimates and comparison chart
- Editable weekday attendance and seat-utilization charts
- Booking no-show, SLA, preventive maintenance, satisfaction and cost KPIs
- Implementation plan

## Important
All default weekday attendance, bookings, requests, maintenance and cost values are illustrative. They are not actual MoveInSync data. Replace them with validated data before using the dashboard operationally.

## Run locally on Windows
```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\activate
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

## Deploy
Push `app.py`, `requirements.txt` and `README.md` to a GitHub repository, then deploy `app.py` using Streamlit Community Cloud.

Suggested repository name: `moveinsync-workplace-operations`

This is an independent demonstration project and is not affiliated with or endorsed by MoveInSync.
