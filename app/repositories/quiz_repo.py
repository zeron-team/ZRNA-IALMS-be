# backend/app/repositories/quiz_repo.py

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from app import db_models
from typing import Optional


def create_quiz_for_module(db: Session, module_id: int, questions_data: list):
    """Crea las preguntas y opciones para el quiz de un módulo."""
    for q_data in questions_data:
        db_question = db_models.Question(
            module_id=module_id,
            question_text=q_data.get('question_text', 'Sin texto')
        )
        db.add(db_question)
        db.flush()

        options = q_data.get('options', [])
        if not options: continue

        for o_data in options:
            db_option = db_models.Option(
                question_id=db_question.id,
                option_text=o_data.get('option_text', 'Sin opción'),
                is_correct=o_data.get('is_correct', False)
            )
            db.add(db_option)
    db.commit()

def get_quiz_for_module(db: Session, module_id: int):
    """Obtiene todas las preguntas y sus opciones para un módulo específico."""
    return db.query(db_models.Question).options(
        joinedload(db_models.Question.options)
    ).filter(db_models.Question.module_id == module_id).all()

# --- ESTAS SON LAS FUNCIONES QUE FALTAN ---
def get_correct_answers_for_module(db: Session, module_id: int) -> dict:
    """Obtiene un diccionario de {question_id: correct_option_id} para un módulo."""
    questions = get_quiz_for_module(db, module_id)
    correct_answers = {}
    for question in questions:
        for option in question.options:
            if option.is_correct:
                correct_answers[question.id] = option.id
                break
    return correct_answers

def create_quiz_attempt(db: Session, user_id: int, module_id: int, score: float, passed: bool):
    """Guarda un intento de quiz en la base de datos."""
    attempt = db_models.QuizAttempt(
        user_id=user_id,
        module_id=module_id,
        score=score,
        passed=passed
    )
    db.add(attempt)
    db.commit()


def get_average_quiz_score(db: Session, user_id: int, course_id: int) -> Optional[float]:
    """
    Calcula el puntaje promedio de los quizzes de un usuario para un curso específico.
    """
    avg_score = db.query(func.avg(db_models.QuizAttempt.score)).join(
        db_models.Module
    ).filter(
        db_models.QuizAttempt.user_id == user_id,
        db_models.Module.course_id == course_id
    ).scalar()

    return avg_score

def count_quiz_attempts(db: Session, user_id: int, module_id: int) -> int:
    """Cuenta el número de intentos para un quiz por un usuario."""
    return db.query(db_models.QuizAttempt).filter(
        db_models.QuizAttempt.user_id == user_id,
        db_models.QuizAttempt.module_id == module_id
    ).count()