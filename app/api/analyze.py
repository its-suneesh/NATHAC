from fastapi import APIRouter

from app.models.schemas import AnalyzeRequest, AnalysisResponse
from app.services.processor import process_student_risk
from app.core.logging_config import app_logger, error_logger

router = APIRouter(prefix="/api/v1", tags=["NATHAC"])


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_student(request: AnalyzeRequest):

    app_logger.info(
        f"Analysis request received | Student={request.student.student_id}"
    )

    try:
        response = await process_student_risk(
            request.student,
            request.dependencies
        )

        app_logger.info(
            f"Analysis completed | Student={request.student.student_id} "
            f"| Subjects={len(response.subject_outcomes)}"
        )

        return response

    except Exception as e:
        error_logger.error(
            f"Analysis failed | Student={request.student.student_id} | Error={e}"
        )
        raise
