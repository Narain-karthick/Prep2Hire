# 🚀 Prep2Hire – AI Powered Mock Interview Platform

Prep2Hire is a **full-stack AI-powered mock interview platform** built for hackathons and interview preparation.  
It simulates a **real technical interview** with adaptive difficulty, time constraints, scoring, and actionable feedback — using **only HTML, CSS, Vanilla JS, and FastAPI**.

---

## 🎥 Demo Video
🔗  https://drive.google.com/file/d/1nw1d1ZmY925Qg6P7ynBwiWzVDnij0kcg/view?usp=sharing

## 🧠 Features

### ✅ Resume & Job Description Analysis
- Upload resume (PDF / TXT)
- Paste job description (tech roles)
- Extracts:
  - Skills
  - Experience
  - Role level
- Computes **skill match percentage**

### 🎤 AI Mock Interview (Rule-Based)
- No external AI API required
- Question flow:
  - Easy → Medium → Hard
- Question types:
  - Technical
  - Conceptual
  - Behavioral
  - Scenario-based

### 📈 Adaptive Difficulty
- Score > 75 → Increase difficulty
- Score 40–75 → Maintain difficulty
- Score < 40 → Decrease difficulty

### ⏱️ Time-Bound Answers
- Fixed time per question (configurable)
- Countdown timer
- Auto-submit on timeout

### 🛑 Early Termination
- Interview ends early if last 3 scores average < 30
- Clear termination reason provided

### 📊 Scoring Engine
Each answer is evaluated on:
- Accuracy
- Clarity
- Depth
- Relevance
- Time efficiency  

Returns structured JSON scores.

### 🧾 Final Interview Report
- Interview Readiness Score (0–100)
- Skill-wise breakdown
- Strengths & weaknesses
- Actionable feedback
- Hiring readiness indicator

---

## 🧱 Tech Stack

### Frontend (STRICT)
- HTML
- CSS
- Vanilla JavaScript  
❌ No React / Vue / Angular / frameworks

### Backend
- Python
- FastAPI
- Uvicorn

---

## 📁 Project Structure

Prep2Hire/
├── backend/
│ ├── main.py
│ ├── resume_parser.py
│ ├── jd_parser.py
│ ├── interview_engine.py
│ ├── scoring_engine.py
│ └── requirements.txt
│
├── frontend/
│ ├── index.html
│ ├── style.css
│ └── app.js
│
└── README.md

## ▶️ How to Run

### Backend
```bash
pip install -r backend/requirements.txt
uvicorn backend.main:app --reload
```


## Run Frontend
Open frontend/index.html
Use Live Server (recommended)


🎯 Purpose

Prep2Hire helps students and job seekers practice interviews in a realistic, structured, and measurable way — perfect for hackathons, placements, and self-preparation.


## 👨‍💻 Author
Narain Karthick
Built for hackathons and interview practice
