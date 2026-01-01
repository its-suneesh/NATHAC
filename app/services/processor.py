import asyncio
from app.models.schemas import SubjectOutcome, AnalysisResponse
from app.services.llm_service import get_llm_provider
from app.core.logging_config import app_logger, error_logger

async def process_student_risk(request_data, provider_name: str = None):
    """
    Orchestrates the parallel risk analysis.
    1. Extracts student history (CoursesStudied).
    2. Creates async tasks for each target subject (CoursesToStudy).
    3. Aggregates results.
    """
    
    student = request_data.student_data
    
    app_logger.info(
        f"Starting parallel analysis | Student={student.StudentID} | "
        f"SubjectCount={len(student.CoursesToStudyData)} | Provider={provider_name}"
    )

    try:
        llm_service = get_llm_provider(provider_name)
    except Exception as e:
        error_logger.critical(f"Failed to initialize LLM service: {e}")
        raise

    history_dicts = [h.dict() for h in student.CoursesStudiedData]

    tasks = []
    for course_to_study in student.CoursesToStudyData:
        task = llm_service.analyze(
            target_paper=course_to_study.dict(),
            history=history_dicts
        )
        tasks.append(task)

    try:
        raw_results = await asyncio.gather(*tasks, return_exceptions=True)
    except Exception as e:
        error_logger.critical(f"Critical failure during async gather: {e}")
        raise

    subject_outcomes = []
    
    for i, result in enumerate(raw_results):
        original_course = student.CoursesToStudyData[i]

        if isinstance(result, Exception):
            error_logger.error(
                f"Task failed for subject {original_course.PaperCode}: {result}"
            )
            subject_outcomes.append(SubjectOutcome(
                paper_name=original_course.PaperName,
                paper_code=original_course.PaperCode,
                risk_level="Unknown",
                key_signals=[],
                risk_drivers=["Internal Analysis Error"],
                recommended_focus=["Contact administrator"]
            ))
        else:
            try:
                outcome = SubjectOutcome(**result)
                subject_outcomes.append(outcome)
            except Exception as validation_err:
                error_logger.error(f"Schema validation failed for AI response: {validation_err}")
                subject_outcomes.append(SubjectOutcome(
                    paper_name=original_course.PaperName,
                    paper_code=original_course.PaperCode,
                    risk_level="Unknown",
                    key_signals=[],
                    risk_drivers=["Data Format Error"],
                    recommended_focus=[]
                ))

    app_logger.info(f"Analysis completed successfully | Student={student.StudentID}")

    return AnalysisResponse(
        student_id=student.StudentID,
        studentsemesteryerrid=student.StudentSemesterYearID,
        subject_outcomes=subject_outcomes
    )