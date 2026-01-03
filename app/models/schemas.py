from typing import List, Optional, Literal, Any
from pydantic import BaseModel, Field



class DependencyData(BaseModel):
    DependencyCourseName: str
    DependencyCourseCode: str
    Weightage: str
    Reason: str

class CourseToStudy(BaseModel):
    PaperName: str
    PaperCode: str
    PaperNameID: int
    SemesterYearStudentID: int
    DependencyCourseData: List[DependencyData] = []
    model_config = {"extra": "ignore"}

class CourseStudied(BaseModel):
    PaperName: str
    PaperCode: str
    InternalMark: float
    InternalMaxMark: Optional[float] = 0.0
    ExternalMark: float
    ExternalMaxMark: Optional[float] = 0.0
    SemesterName: Optional[str] = None
    MarkOrGrade: Optional[Any] = None 
    model_config = {"extra": "ignore"}

class StudentRequestData(BaseModel):
    StudentName: str
    StudentID: str
    SemesterYearStudentID: str
    AdmissionNo: Optional[str]
    RegisterNo: Optional[str]
    CourseName: Optional[str]
    CoursesToStudyData: List[CourseToStudy]
    CoursesStudiedData: List[CourseStudied]

class AnalyzeRequest(BaseModel):
    student_data: StudentRequestData
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