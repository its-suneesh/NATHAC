import asyncio
from typing import List
from app.services.llm_service import get_llm_provider
from app.models.schemas import StudentRequestData, AnalysisResponse, SubjectOutcome
from app.core.logging_config import app_logger

async def process_student_risk(student_data: StudentRequestData, provider_name: str) -> AnalysisResponse:
    """
    Orchestrates risk analysis. 
    Now accepts valid StudentRequestData directly.
    """
    
    llm_service = get_llm_provider(provider_name)

    history_data = [
        course.model_dump() for course in student_data.CoursesStudiedData
    ]
    
    courses_to_analyze = student_data.CoursesToStudyData
    
    app_logger.info(f"Starting analysis for {len(courses_to_analyze)} courses.")

    tasks = []
    for course in courses_to_analyze:
        tasks.append(
            llm_service.analyze(
                target_paper=course.model_dump(),
                history=history_data
            )
        )

    try:
        results = await asyncio.gather(*tasks)

    except Exception as e:
        raise RuntimeError(f"Failed during batch processing: {str(e)}") from e

    subject_outcomes = [SubjectOutcome(**res) for res in results]

    return AnalysisResponse(
        student_id=str(student_data.StudentID),
        studentsemesteryerrid=str(student_data.SemesterYearStudentID),
        subject_outcomes=subject_outcomes
    )