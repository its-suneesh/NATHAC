from uuid import uuid4
from app.models.schemas import SubjectOutcome, AnalysisResponse
from app.services.llm_service import get_llm_provider
from app.core.logging_config import app_logger, error_logger


async def process_student_risk(student, dependencies, provider_name: str = None):
    """
    Orchestrates the risk analysis process.
    - Selects the correct AI provider (Gemini/DeepSeek/OpenAI).
    - Filters student history for each target subject.
    - Calls the AI asynchronously.
    """

    app_logger.info(
        f"Processing analysis started | Student={student.student_id} | Model={provider_name}"
    )

    try:
        llm_service = get_llm_provider(provider_name)
    except Exception as e:
        error_logger.error(f"Failed to initialize LLM Provider: {e}")
        raise

    subject_outcomes = []

    for subject in dependencies.subjects_to_predict:

        app_logger.info(
            f"Analyzing subject={subject.subject_code} "
            f"| DependencyCount={len(subject.dependencies)}"
        )

        try:
            dependency_codes = {
                dep.subject_code for dep in subject.dependencies
            }

            filtered_history = [
                record.dict() for record in student.academic_history
                if record.subject_code in dependency_codes
            ]

            app_logger.info(
                f"Filtered history size={len(filtered_history)} "
                f"| Subject={subject.subject_code}"
            )

            if not filtered_history:
                app_logger.warning(
                    f"Skipping AI analysis: No matching history found for {subject.subject_code}"
                )
                continue

            raw_result = await llm_service.analyze(
                subject.subject_code,
                filtered_history
            )
            
            outcome = SubjectOutcome(**raw_result)
            subject_outcomes.append(outcome)

        except Exception as e:
            error_logger.error(
                f"Subject analysis failed | "
                f"Student={student.student_id} | "
                f"Subject={subject.subject_code} | Error={e}"
            )
            continue

    app_logger.info(
        f"Processing analysis completed | Student={student.student_id}"
    )

    return AnalysisResponse(
        analysis_id=str(uuid4()),
        student_id=student.student_id,
        subjects_requested=[
            s.subject_code for s in dependencies.subjects_to_predict
        ],
        subject_outcomes=subject_outcomes
    )