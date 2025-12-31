from typing import List, Optional, Literal
from pydantic import BaseModel


# -------------------------
# Student Performance Input
# -------------------------

class InternalScore(BaseModel):
    name: str
    score: float
    max: float


class ExternalScore(BaseModel):
    score: float
    max: float


class SubjectHistory(BaseModel):
    subject_code: str
    semester: Optional[int] = None
    internal: List[InternalScore]
    external: ExternalScore
    final_grade: Optional[str] = None


class StudentHistory(BaseModel):
    student_id: str
    academic_history: List[SubjectHistory]


# -------------------------
# Dependency Input (TCS)
# -------------------------

class Dependency(BaseModel):
    subject_code: str
    weight: float
    reason: Optional[str] = None


class SubjectDependency(BaseModel):
    subject_code: str
    dependencies: List[Dependency]


class DependencyRequest(BaseModel):
    subjects_to_predict: List[SubjectDependency]


# -------------------------
# Output Models
# -------------------------
class KeySignal(BaseModel):
    signal: str
    description: str

class SubjectOutcome(BaseModel):
    subject_code: str
    risk_level: str
    key_signals: List[KeySignal]   
    risk_drivers: List[str]
    recommended_focus: List[str]


class AnalysisResponse(BaseModel):
    analysis_id: str
    student_id: str
    subjects_requested: List[str]
    subject_outcomes: List[SubjectOutcome]
    
class AnalyzeRequest(BaseModel):
    student: StudentHistory
    dependencies: DependencyRequest
    model: Literal["openai", "gemini", "deepseek"] = "gemini"
    