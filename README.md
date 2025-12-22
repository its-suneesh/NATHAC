

# 🧠 NATHAC – Academic Risk Analysis System

NATHAC is an **AI-powered academic risk analysis system** built using **FastAPI** and **Google Gemini AI**.
It analyzes a student’s **prerequisite subject performance** to predict the **risk level** for future subjects and provides **actionable academic recommendations**.

---

## ✨ Key Features

* 🚀 **FastAPI-based REST API**
* 🤖 **Gemini AI integration** (`gemini-2.5-flash`)
* 🔐 **JWT Authentication** (login → access token)
* 🧵 **Async, non-blocking AI calls** (no hanging requests)
* 🧪 **Structured request & response schemas**
* 📊 **Prerequisite-based academic risk analysis**
* 📝 **Centralized logging with rotating log files**
* 🧱 **Clean, scalable project structure**

---

## 🗂️ Project Structure

```
nathac/
│
├── app/
│   ├── api/
│   │   ├── analyze.py        # Protected analysis endpoint
│   │   └── auth.py           # Login & token generation
│   │
│   ├── core/
│   │   ├── config.py         # Environment configuration
│   │   ├── security.py       # JWT create & verify
│   │   ├── dependencies.py  # Auth dependency
│   │   └── logging_config.py# Logging setup
│   │
│   ├── models/
│   │   └── schemas.py        # Pydantic models
│   │
│   ├── services/
│   │   ├── processor.py     # Core analysis workflow
│   │   └── llm_service.py   # Async Gemini AI calls
│   │
│   └── main.py               # FastAPI app entry point
│
├── logs/
│   ├── app.log               # Application logs
│   └── error.log             # Error logs
│
├── .env                      # Environment variables (not committed)
├── .gitignore
├── requirements.txt
└── README.md
```

---

## 🔐 Authentication Flow (JWT)

1. **Login** using username & password
2. Receive **JWT access token**
3. Use token to access protected endpoints

### Login Endpoint

```
POST /auth/login
```

**Request**

```json
{
  "username": "admin",
  "password": "admin123"
}
```

**Response**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

---

## 🧠 Academic Risk Analysis Endpoint

### Protected Endpoint

```
POST /api/v1/analyze
```

### Headers

```
Authorization: Bearer <access_token>
```

### Request Body (Example)

```json
{
  "student": {
    "student_id": "S001",
    "academic_history": [
      {
        "subject_code": "CS101",
        "semester": 1,
        "internal": [
          { "name": "Midterm", "score": 18, "max": 25 }
        ],
        "external": { "score": 42, "max": 60 },
        "final_grade": "B"
      }
    ]
  },
  "dependencies": {
    "subjects_to_predict": [
      {
        "subject_code": "CS301",
        "dependencies": [
          {
            "subject_code": "CS101",
            "weight": 0.4,
            "reason": "Programming fundamentals"
          }
        ]
      }
    ]
  }
}
```

### Response (Example)

```json
{
  "analysis_id": "e7f1d5c4-8c1f-4e2b-a9b1-9d9b7f13aabc",
  "student_id": "S001",
  "subjects_requested": ["CS301"],
  "subject_outcomes": [
    {
      "subject_code": "CS301",
      "risk_level": "Medium",
      "key_signals": [
        {
          "signal": "Weak loop concepts",
          "description": "Moderate performance in CS101"
        }
      ],
      "risk_drivers": ["Low internal score in CS101"],
      "recommended_focus": ["Practice basic programming problems"]
    }
  ]
}
```

---

## ⚙️ Environment Configuration

Create a `.env` file in the root directory:

```env
GEMINI_API_KEY=your_gemini_api_key_here
JWT_SECRET_KEY=your_strong_random_secret_here
```

> ⚠️ Never commit `.env` to GitHub.

## 📦 Requirements

Install dependencies:

```bash
pip install -r requirements.txt
```
## ▶️ Running the Application

```bash
uvicorn app.main:app --reload
```

Open Swagger UI:

```
http://127.0.0.1:8000/
```