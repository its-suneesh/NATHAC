from uuid import uuid4

from app.models.schemas import SubjectOutcome, AnalysisResponse
from app.services.llm_service import analyze_with_ai
from app.core.logging_config import app_logger, error_logger


# -------------------------------------------------
# Main processing logic (ASYNC)
# -------------------------------------------------
async def process_student_risk(student, dependencies):

    app_logger.info(
        f"Processing analysis started | Student={student.student_id}"
    )

    subject_outcomes = []

    for subject in dependencies.subjects_to_predict:

        app_logger.info(
            f"Analyzing subject={subject.subject_code} "
            f"| DependencyCount={len(subject.dependencies)}"
        )

        try:
            # Extract prerequisite subject codes
            dependency_codes = {
                dep.subject_code for dep in subject.dependencies
            }

            # Filter student history for prerequisite subjects
            filtered_history = [
                record for record in student.academic_history
                if record.subject_code in dependency_codes
            ]

            app_logger.info(
                f"Filtered history size={len(filtered_history)} "
                f"| Subject={subject.subject_code}"
            )

            # ---- ASYNC AI CALL ----
            raw_result = await analyze_with_ai(
                subject.subject_code,
                filtered_history
            )

            # Validate AI output
            outcome = SubjectOutcome(**raw_result)
            subject_outcomes.append(outcome)

        except Exception as e:
            error_logger.error(
                f"Subject analysis failed | "
                f"Student={student.student_id} | "
                f"Subject={subject.subject_code} | Error={e}"
            )
            raise

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
