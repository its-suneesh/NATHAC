from fastapi import APIRouter, Depends

from app.models.schemas import AnalyzeRequest, AnalysisResponse
from app.services.processor import process_student_risk
from app.core.logging_config import app_logger, error_logger
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/api/v1", tags=["NATHAC"])


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_student(
    request: AnalyzeRequest,
    current_user: str = Depends(get_current_user)
):

    app_logger.info(
        f"Analysis request received | Student={request.student.student_id} "
        f"| RequestedBy={current_user} | Model={request.model_provider}"
    )

    try:
        response = await process_student_risk(
            request.student,
            request.dependencies,
            provider_name=request.model_provider
        )

        app_logger.info(
            f"Analysis completed | Student={request.student.student_id} "
            f"| RequestedBy={current_user}"
        )

        return response

    except Exception as e:
        error_logger.error(
            f"Analysis failed | RequestedBy={current_user} | Error={e}"
        )
        raise