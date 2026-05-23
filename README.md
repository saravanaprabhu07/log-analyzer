Intelligent Log Analyzer

A lightweight, full-stack web application that automates 
server log analysis using Python FastAPI and React.js.

What it does
 Upload any .log file via REST API
 Automatically categorizes logs into ERROR, WARNING, INFO
 Calculates real-time system health score (%)
 Stores all results in SQLite database
 Displays interactive dashboard with bar charts
 Filter logs by severity level

Tech Stack
 Backend: Python, FastAPI, SQLAlchemy, SQLite, Uvicorn  
 Frontend: React.js, Recharts, CSS3  
 API: REST, JSON, Swagger UI  

Quick Start
Backend
 cd log-analyzer
 source venv/bin/activate
 uvicorn main:app --reload

Frontend
 cd frontend
 npm install
 npm start

Live
 Backend API  → http://127.0.0.1:8000/docs  
 Dashboard    → http://localhost:3000

Why I built this
 Enterprise log tools like Splunk and ELK Stack are 
expensive and complex. This project provides a free, 
lightweight alternative deployable in under 2 minutes.
