# backend/app/routers/quizzes.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.services import ai_service
from app.dependencies import get_db
from app.repositories import quiz_repo, progress_repo, module_repo, course_repo
from app.security import get_current_active_user
from app.models.user import User as UserSchema
from app.models.quiz import QuizSchema, QuizSubmission, QuizResultDetailed, QuizStatus
from app.logic import course_logic

router = APIRouter(
    prefix="/quizzes",
    tags=["Quizzes"]
)


@router.get("/module/{module_id}", response_model=QuizSchema)
def read_quiz_for_module(module_id: int, db: Session = Depends(get_db)):
    """
    Obtiene las preguntas y opciones para el quiz de un módulo.
    """
    questions = quiz_repo.get_quiz_for_module(db, module_id=module_id)
    if not questions:
        raise HTTPException(status_code=404, detail="Quiz no encontrado para este módulo.")

    # Simplemente devuelve un diccionario que coincide con el schema.
    # FastAPI se encargará de la conversión y validación.
    return {"module_id": module_id, "questions": questions}


@router.post("/module/{module_id}/submit", response_model=QuizResultDetailed)
def submit_quiz(
        module_id: int,
        submission: QuizSubmission,
        db: Session = Depends(get_db),
        current_user: UserSchema = Depends(get_current_active_user)
):
    # Restriction removed: No limit on quiz attempts

    correct_answers = quiz_repo.get_correct_answers_for_module(db, module_id)
    score_count = 0
    detailed_results = []
    for q_id, user_opt_id in submission.answers.items():
        correct_opt_id = correct_answers.get(int(q_id))
        is_correct = (int(user_opt_id) == correct_opt_id)
        if is_correct:
            score_count += 1
        detailed_results.append({
            "question_id": int(q_id), "user_option_id": int(user_opt_id),
            "correct_option_id": correct_opt_id, "is_correct": is_correct
        })

    total_questions = len(correct_answers)
    final_score = round((score_count / total_questions) * 100) if total_questions > 0 else 0
    passed = final_score >= 55

    quiz_repo.create_quiz_attempt(db, user_id=current_user.id, module_id=module_id, score=final_score, passed=passed)

    if passed:
        progress_repo.mark_module_as_completed(db, user_id=current_user.id, module_id=module_id)

    # --- LÓGICA AÑADIDA Y CORREGIDA ---
    motivational_phrase = ai_service.generate_motivational_phrase(final_score, passed)

    module = module_repo.get_module_by_id(db, module_id)
    course = course_repo.get_course_by_id(db, module.course_id)
    total_stars, earned_stars = course_logic.calculate_star_rating(db, course, current_user.id)

    incorrect_count = total_questions - score_count
    return {
        "score": final_score,
        "passed": passed,
        "total_questions": total_questions,
        "correct_count": score_count,
        "incorrect_count": incorrect_count,
        "detailed_results": detailed_results,
        "motivational_phrase": motivational_phrase,
        "course_total_stars": total_stars,
        "course_earned_stars": earned_stars,
        
    }

@router.get("/module/{module_id}/status", response_model=QuizStatus)
def get_quiz_status(
    module_id: int,
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_active_user)
):
    """Verifica si el usuario puede intentar el quiz y cuántos intentos ha hecho."""
    attempts_count = quiz_repo.count_quiz_attempts(db, user_id=current_user.id, module_id=module_id)
    can_attempt = True # Removed attempt limit
    return {
        "can_attempt": can_attempt,
        "attempts_made": attempts_count
    }