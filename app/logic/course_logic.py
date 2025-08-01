# backend/app/logic/course_logic.py

from sqlalchemy.orm import Session
from app.repositories import quiz_repo

def calculate_star_rating(db: Session, course, user_id: int):
    """Calcula las estrellas totales y ganadas para un curso y un usuario."""
    # Regla 1: Estrellas totales según el nivel
    level_map = {"basico": 3, "intermedio": 5, "avanzado": 7}
    total_stars = level_map.get(course.level, 3)

    # Regla 2: Estrellas ganadas según el progreso
    earned_stars = 0
    is_enrolled = any(enrollment.user_id == user_id for enrollment in course.enrollments)

    if is_enrolled:
        avg_score = quiz_repo.get_average_quiz_score(db, user_id, course.id)

        if avg_score is not None:
            if avg_score < 50: # Desaprobado
                earned_stars = 0
            elif avg_score < 75: # Calificación baja
                earned_stars = round(total_stars * 0.33)
            elif avg_score < 95: # Calificación media
                earned_stars = round(total_stars * 0.66)
            else: # Calificación perfecta
                earned_stars = total_stars

    return total_stars, earned_stars