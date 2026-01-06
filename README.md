```markdown
# NATHAC API - Academic Risk Analyzer

A high-performance FastAPI application designed to analyze student academic performance and predict failure risks using Large Language Models (LLMs). It integrates with **Google Gemini**, **OpenAI**, and **DeepSeek** to generate detailed insights based on student history and course dependencies.

## 🚀 Key Features

* **Multi-LLM Support:** Seamlessly switch between Gemini 1.5, GPT-4, and DeepSeek.
* **Production Optimized:** Implements connection pooling (`httpx`), concurrency limits (`asyncio.Semaphore`), and caching.
* **Secure:** JWT Authentication and environment-based configuration.
* **Docker Ready:** Fully containerized with non-root user security and Gunicorn workers.

---

## 🛠️ Setup & Installation

### 1. Prerequisites
* Docker & Docker Compose
* Python 3.11+ (for local development)

### 2. Environment Configuration
Create a `.env` file in the root directory:

```ini
# Security
JWT_SECRET_KEY=your_super_secret_jwt_key
USERNAME=admin
PASSWORD=your_secure_password
ACCESS_TOKEN_EXPIRE_HOURS=24

# LLM Keys (Add at least one)
GEMINI_API_KEY=your_gemini_key
GEMINI_MODEL=gemini-1.5-flash

OPENAI_API_KEY=your_openai_key
OPENAI_MODEL=gpt-4-turbo

DEEPSEEK_API_KEY=your_deepseek_key
DEEPSEEK_MODEL=deepseek-chat

```

### 3. Running with Docker (Recommended)

```bash
docker-compose up --build

```

The API will be available at: `http://localhost:8000`

### 4. Running Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Run server
uvicorn app.main:app --reload

```

---

## 📚 API Endpoints

### 1. Authentication

**Endpoint:** `POST /auth/login`

Generates a Bearer token required for accessing protected endpoints.

**Request Body:**

```json
{
  "username": "admin",
  "password": "your_secure_password"
}

```

**Response:**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsIn...",
  "token_type": "bearer"
}

```

---

### 2. Analyze Student Risk

**Endpoint:** `POST /api/v1/analyze`

**Headers:**

* `Authorization`: `Bearer <your_access_token>`

**Request Body:**

```json
{
  "url": "[https://external-system.com/api/student/123](https://external-system.com/api/student/123)",
  "model_provider": "gemini" 
}

```

* `url`: A public URL returning the student JSON data (format below).
* `model_provider`: Options: `"gemini"`, `"openai"`, `"deepseek"`. (Default: `"gemini"`)

**Response:**

```json
{
  "StudentID": "101",
  "SemesterYearStudentID": "2024-S1",
  "subject_outcomes": [
    {
      "paper_name": "Data Structures",
      "paper_code": "CS201",
      "risk_level": "High",
      "key_signals": [
        {
          "signal": "Prerequisite Failure",
          "description": "Failed C Programming which has 5/5 weightage."
        }
      ],
      "risk_drivers": [
        "Low internal marks (12/50)",
        "History of struggling with logic-based subjects"
      ],
      "recommended_focus": [
        "Retake C Programming concepts",
        "Focus on pointer arithmetic exercises"
      ]
    }
  ]
}

```

---

## 📄 External Data Format (The URL)

The `url` you provide in the analyze request **must** return a JSON object (or list containing one object) with this structure:

```json
{
  "StudentName": "John Doe",
  "StudentID": "101",
  "SemesterYearStudentID": "2024-S1",
  
  "CoursesToStudyData": [
    {
      "PaperName": "Advanced Python",
      "PaperCode": "CS305",
      "PaperNameID": 501,
      "SemesterYearStudentID": 2024,
      "DependencyCourseData": [
        {
          "DependencyCourseName": "Basic Python",
          "DependencyCourseCode": "CS101",
          "Weightage": "5",
          "Reason": "Core syntax required"
        }
      ]
    }
  ],
  
  "CoursesStudiedData": [
    {
      "PaperName": "Basic Python",
      "PaperCode": "CS101",
      "PaperNameID": 101,
      "SemesterYearStudentID": "2023-S1",
      "InternalMark": 45.0,
      "InternalMaxMark": 50.0,
      "ExternalMark": 30.0,
      "ExternalMaxMark": 100.0,
      "GradeObtained": "B",
      "MarkOrGrade": "Grade"
    }
  ]
}

```

```