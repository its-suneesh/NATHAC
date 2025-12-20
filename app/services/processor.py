import uuid
from app.models.schemas import (
    StudentHistory,
    DependencyRequest,
    AnalysisResponse,
    SubjectOutcome
)
from app.services.llm_service import analyze_with_ai


def process_student_risk(
    student: StudentHistory,
    dependencies: DependencyRequest
) -> AnalysisResponse:

    subject_outcomes = []

    for subject in dependencies.subjects_to_predict:
        dependency_codes = {
            dep.subject_code for dep in subject.dependencies
        }

        # -------------------------
        # FILTER STUDENT HISTORY
        # -------------------------
        filtered_history = [
            record
            for record in student.academic_history
            if record.subject_code in dependency_codes
        ]

        raw_result  = analyze_with_ai(
            subject_code=subject.subject_code,
            filtered_history=filtered_history
        )
        
        outcome = SubjectOutcome(**raw_result)
        subject_outcomes.append(outcome)

    return AnalysisResponse(
        analysis_id=f"NATHAC-ANL-{uuid.uuid4().hex[:6].upper()}",
        student_id=student.student_id,
        subjects_requested=[
            s.subject_code for s in dependencies.subjects_to_predict
        ],
        subject_outcomes=subject_outcomes
    )
