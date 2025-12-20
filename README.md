# NATHAC: Networked Academic Thinking & Holistic Analysis Core

NATHAC is a FastAPI-powered analysis engine that uses AI to predict a student's risk level in a target subject by analyzing their performance in prerequisite subjects.

---

## 🛠 Setup & Environment

The project uses `pydantic-settings` to manage configuration via a `.env` file.

1. **Create a `.env` file** in the root directory:
```bash
touch .env

```


2. **Add your Gemini API Key**:
Open the `.env` file and add the following variables:
```env
NATHAC_ENV="dev"
GEMINI_API_KEY="your_actual_gemini_api_key_here"

```

* **GEMINI_API_KEY**: Your secret key from Google AI Studio.

---

## 🚀 How to Run

Ensure you have the required dependencies installed (FastAPI, Pydantic, Uvicorn, and Google Generative AI).

1. **Start the server**:
```bash
uvicorn main:app --reload

```


2. **Access the API**:
The server will run at `http://127.0.0.1:8000`.

---

## 🔍 How to Check (Endpoints)

FastAPI automatically generates interactive documentation for testing.

### 1. Interactive Documentation (Swagger UI)

Go to: **`http://127.0.0.1:8000/docs`**
This provides a visual interface to send test requests and view the exact JSON schema required.

### 2. Main Endpoint

* **POST** `/api/v1/analyze`
* **Description**: Analyzes a student's history against prerequisite "dependencies" to generate a risk report.

---

## 📝 Example Request Body

To check the endpoint manually (e.g., via Postman or the `/docs` page), use this JSON format:

```json
{
  "student": {
    "student_id": "STU123",
    "academic_history": [
      {
        "subject_code": "MATH101",
        "internal": [{"name": "Quiz", "score": 85, "max": 100}],
        "external": {"score": 78, "max": 100}
      }
    ]
  },
  "dependencies": {
    "subjects_to_predict": [
      {
        "subject_code": "PHYS201",
        "dependencies": [
          {"subject_code": "MATH101", "weight": 1.0, "reason": "Calculus base"}
        ]
      }
    ]
  }
}

```
