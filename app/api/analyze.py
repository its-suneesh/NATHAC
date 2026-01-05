import httpx
from fastapi import APIRouter, Depends, HTTPException, Request
from app.models.schemas import AnalyzeRequest, AnalysisResponse, StudentRequestData
from app.services.processor import process_student_risk
from app.core.logging_config import app_logger, error_logger
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/api/v1", tags=["NATHAC"])


async def fetch_student_data_from_url(url: str, client: httpx.AsyncClient) -> StudentRequestData:
    """
    Fetches JSON data using the SHARED HTTP client.
    """
    try:
        app_logger.info(f"Fetching student data from: {url}")
        response = await client.get(str(url))
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=400, 
                detail=f"External URL returned status {response.status_code}"
            )

        data = response.json()

        if isinstance(data, list) and len(data) > 0:
            student_raw = data[0]
        elif isinstance(data, dict):
            student_raw = data
        else:
            raise ValueError("External API returned unexpected JSON format (expected list or dict)")

        student_data = StudentRequestData(**student_raw)
        return student_data

    except httpx.RequestError as e:
        error_logger.error(f"Network error fetching data: {e}")
        raise HTTPException(status_code=502, detail="Failed to connect to external student data source")
    
    except ValueError as e:
        error_logger.error(f"Data validation error: {e}")
        raise HTTPException(status_code=422, detail=f"Invalid student data structure: {str(e)}")

@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_student(
    request: AnalyzeRequest,
    req_obj: Request, 
    current_user: str = Depends(get_current_user)
):
    """
    Endpoint to analyze student academic risk.
    """
    try:
        shared_client = req_obj.app.state.http_client
        
        student_data = await fetch_student_data_from_url(request.url, shared_client)
        
        app_logger.info(
            f"API Request | User={current_user} | StudentID={student_data.StudentID} | Model={request.model_provider}"
        )

        response = await process_student_risk(
            student_data=student_data,
            provider_name=request.model_provider
        )

        return response

    except HTTPException as he:
        raise he

    except RuntimeError as re:
        error_logger.error(f"LLM Service Error: {str(re)}")
        raise HTTPException(
            status_code=503, 
            detail=f"AI Service Unavailable: {str(re)}"
        )

    except Exception as e:
        error_logger.error(f"Critical System Error | User={current_user} | Error={str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error during analysis")