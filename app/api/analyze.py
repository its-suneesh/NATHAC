from fastapi import APIRouter
from app.models.schemas import (
    AnalyzeRequest,
    StudentHistory,
    DependencyRequest,
    AnalysisResponse
)
from app.services.processor import process_student_risk

router = APIRouter(prefix="/api/v1", tags=["NATHAC"])


@router.post("/analyze", response_model=AnalysisResponse)
def analyze_student(request: AnalyzeRequest):
    return process_student_risk(
        request.student,
        request.dependencies
    )

