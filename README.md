# 🧠 AI Task Assignment System (Flask + Docker + MySQL)

This project is an AI-powered task assignment system that matches tasks to the most suitable employee based on skill match and workload. It supports both rule-based and LLM-based (via Ollama/Mistral) task assignment.

---

## 🗂 Project Structure

task-agent/
├── backend/
│ ├── app.py # Flask backend with endpoints and logic
│ ├── requirements.txt # Python dependencies
│ └── Dockerfile # Docker setup for backend
│
├── frontend/
│ └── index.html # Static frontend (optional UI)
│
├── database/
│ ├── init.sql # SQL schema for employees and tasks
│ ├── employees.json # Sample employee data
│ ├── tasks.json # Sample task data
│
├── docker-compose.yml # Orchestrates backend and MySQL services
├── .gitignore # Ignored files (e.g. venv, pycache)
└── README.md # You're reading it!

yaml
Copy
Edit

---

## 🚀 Features

- 🧠 AI-based employee selection using **Mistral via Ollama**
- ⚙️ Rule-based fallback assignment logic
- 🐳 Dockerized with `docker-compose`
- 🗃️ MySQL integration for persistent task and employee storage
- 🧪 API testable with Postman

---

## 🛠️ How to Run

### 1. Start the Docker environment:

```bash
docker-compose up --build
2. Access the Flask backend
Visit: http://localhost:5000

You should see:

✅ Flask backend is running on Docker!

📬 API Endpoints
POST /assign-task
Assign a task using the LLM model.

json
Copy
Edit
{
  "title": "Write Report",
  "skills": "python, flask",
  "priority": "high"
}
POST /assign-rule-based
Assign a task using rules (skills + workload).

📦 Environment Variables
These can be configured in your Docker container:

ini
Copy
Edit
DB_HOST=task-agent-db
DB_PORT=3306
DB_USER=root
DB_PASSWORD=root123
DB_NAME=task_agent
💡 Notes
Ollama must be running locally to support LLM-based assignment (http://localhost:11434).

If not running, the system falls back gracefully to rule-based logic.

🤝 Contributing
Pull requests and issue reports are welcome!

