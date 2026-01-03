from typing import List, Optional, Literal, Any
from pydantic import BaseModel, HttpUrl


class DependencyData(BaseModel):
    DependencyCourseName: str = "Unknown"
    DependencyCourseCode: str = "Unknown"
    Weightage: Optional[str] = "N/A"
    Reason: Optional[str] = "N/A"
    model_config = {"extra": "ignore"}

class CourseToStudy(BaseModel):
    PaperName: str
    PaperCode: str
    CourseOutComes: Optional[str] = None
    PaperNameID: int
    SemesterYearStudentID: int
    DependencyCourseData: List[DependencyData] = []
    model_config = {"extra": "ignore"}

class CourseStudied(BaseModel):
    PaperName: str
    PaperCode: str
    SemesterYearStudentID: str
    CourseOutComes: Optional[str] = None
    PaperNameID: int
    InternalMark: float = 0.0
    InternalMaxMark: Optional[float] = 0.0
    InternalGradeObtained: Optional[str] = None
    ExternalMark: float = 0.0
    ExternalMaxMark: Optional[float] = 0.0
    GradeObtained: Optional[str] = None
    SemesterName: Optional[str] = None
    MarkOrGrade: Optional[str] = None 
    model_config = {"extra": "ignore"}

class StudentRequestData(BaseModel):
    StudentName: str
    StudentID: Any
    Batch: Optional[str] = None
    Gender: Optional[str] = None
    Email: Optional[str] = None
    SemesterYearStudentID: Any
    AdmissionNo: Optional[str] = None
    RegisterNo: Optional[str] = None
    CourseName: Optional[str] = None
    CoursesToStudyData: List[CourseToStudy]
    CoursesStudiedData: List[CourseStudied]
    model_config = {"extra": "ignore"}


class AnalyzeRequest(BaseModel):
    url: HttpUrl
    model_provider: Literal["gemini", "openai", "deepseek"] = "gemini"

class KeySignal(BaseModel):
    signal: str
    description: str

class SubjectOutcome(BaseModel):
    paper_name: str
    paper_code: str
    risk_level: str
    key_signals: List[KeySignal]
    risk_drivers: List[str]
    recommended_focus: List[str]

class AnalysisResponse(BaseModel):
    student_id: str
    studentsemesteryerrid: str
    subject_outcomes: List[SubjectOutcome]