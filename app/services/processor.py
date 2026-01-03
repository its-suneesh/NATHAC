import asyncio
from typing import List, Dict, Any
from app.services.llm_service import get_llm_provider
from app.models.schemas import AnalyzeRequest, AnalysisResponse, SubjectOutcome
from app.core.logging_config import app_logger

async def process_student_risk(request_data: AnalyzeRequest, provider_name: str) -> AnalysisResponse:
    """
    Orchestrates the risk analysis by processing all courses in parallel.
    """
    
    llm_service = get_llm_provider(provider_name)
    
    history_data = [
        course.model_dump() for course in request_data.student_data.CoursesStudiedData
    ]
    
    courses_to_analyze = request_data.student_data.CoursesToStudyData
    
    app_logger.info(f"Starting parallel analysis for {len(courses_to_analyze)} courses.")

    tasks = []
    for course in courses_to_analyze:
        tasks.append(
            llm_service.analyze(
                target_paper=course.model_dump(),
                history=history_data
            )
        )

    results = await asyncio.gather(*tasks, return_exceptions=True)

    subject_outcomes: List[SubjectOutcome] = []
    
    for i, result in enumerate(results):
        course_meta = courses_to_analyze[i]
        
        if isinstance(result, Exception):
            app_logger.error(f"Analysis failed for {course_meta.PaperCode}: {str(result)}")
            subject_outcomes.append(
                SubjectOutcome(
                    paper_name=course_meta.PaperName,
                    paper_code=course_meta.PaperCode,
                    risk_level="Unknown",
                    key_signals=[],
                    risk_drivers=["System Error during analysis"],
                    recommended_focus=[]
                )
            )
        else:
            subject_outcomes.append(SubjectOutcome(**result))

    return AnalysisResponse(
        student_id=request_data.student_data.StudentID,
        studentsemesteryerrid=request_data.student_data.SemesterYearStudentID,
        subject_outcomes=subject_outcomes
    )