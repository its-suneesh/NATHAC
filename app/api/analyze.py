from fastapi import APIRouter, Depends, Body, HTTPException
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
    """
    Endpoint to analyze student academic risk.
    Accepts full student history and future courses.
    Returns risk predictions for all requested courses.
    """

    try:
        student_id = request.student_data.StudentID
        provider = request.model_provider
        
        app_logger.info(
            f"API Request | User={current_user} | Student={student_id} | Model={provider}"
        )

        response = await process_student_risk(
            request_data=request,
            provider_name=provider
        )

        return response

    except Exception as e:
        error_logger.error(f"API Endpoint Error | User={current_user} | Error={str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error during analysis")