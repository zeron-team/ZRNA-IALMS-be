# backend/app/repositories/reporting_repo.py

from sqlalchemy.orm import Session, joinedload
from app import db_models

def get_dashboard_stats(db: Session):
    """Calcula estadísticas generales de la plataforma."""
    total_users = db.query(db_models.User).count()
    total_courses = db.query(db_models.Course).count()
    total_enrollments = db.query(db_models.CourseEnrollment).count()
    total_categories = db.query(db_models.Category).count()
    return {
        "total_users": total_users,
        "total_courses": total_courses,
        "total_enrollments": total_enrollments,
        "total_categories": total_categories,
    }

def get_courses_with_enrollments(db: Session):
    """
    Obtiene todos los cursos, cargando explícitamente la relación de inscripciones.
    """
    return db.query(db_models.Course).options(
        joinedload(db_models.Course.enrollments)
    ).all()

def get_rooms_summary_by_instructor(db: Session, instructor_id: int):
    """Obtiene las salas de un instructor y la cantidad de miembros."""
    rooms = db.query(db_models.Room).filter(db_models.Room.instructor_id == instructor_id).all()
    return [{"id": r.id, "name": r.name, "member_count": len(r.members)} for r in rooms]

def get_student_progress_for_instructor_courses(db: Session, instructor_id: int):
    """Obtiene el progreso de los alumnos en los cursos del instructor."""
    # Placeholder - Esta consulta es compleja y se puede desarrollar más adelante
    return []
def get_enrolled_courses_with_progress(db: Session, user_id: int):
    """Obtiene los cursos en los que un usuario está inscrito y su progreso."""
    # Placeholder
    return []

def get_all_student_progress_summary(db: Session, instructor_id: int):
    """
    Obtiene un resumen del progreso de todos los estudiantes de un instructor.
    """
    # Esta es una consulta compleja. Por ahora, devolveremos datos de ejemplo
    # para que puedas construir el frontend.
    return [
        {
            "student_id": 30,
            "student_name": "Renzo Natalio",
            "enrolled_courses_count": 2,
            "rooms_count": 1,
            "overall_progress": 65
        },
        {
            "student_id": 3,
            "student_name": "est",
            "enrolled_courses_count": 1,
            "rooms_count": 1,
            "overall_progress": 20
        }
    ]


def get_detailed_student_progress(db: Session, instructor_id: int):
    """
    Obtiene un reporte detallado del progreso de cada estudiante
    que es miembro de al menos una de las salas del instructor.
    """
    students_in_rooms = db.query(db_models.User).join(
        db_models.RoomMember
    ).join(db_models.Room).filter(
        db_models.Room.instructor_id == instructor_id,
        db_models.User.role_id == 1
    ).options(
        joinedload(db_models.User.profile)  # <-- Carga explícitamente el perfil
    ).distinct().all()

    report = []
    for student in students_in_rooms:
        # --- CORRECCIÓN: Maneja el caso de que el perfil sea None ---
        student_name = (student.profile.first_name if student.profile else student.username)

        student_data = {
            "student_id": student.id,
            "student_name": student_name,
            "enrollments": []
        }

        # Buscamos los cursos en los que el estudiante está inscrito
        enrollments = db.query(db_models.CourseEnrollment).filter(
            db_models.CourseEnrollment.user_id == student.id
        ).all()

        for enrollment in enrollments:
            course = enrollment.course

            # Verificamos si este curso pertenece a una de las salas del instructor
            room = db.query(db_models.Room).join(db_models.RoomCourse).filter(
                db_models.Room.instructor_id == instructor_id,
                db_models.RoomCourse.course_id == course.id,
            ).first()

            # Calculamos el progreso para ese curso
            total_modules = len(course.modules)
            completed_modules = db.query(db_models.StudentProgress).filter(
                db_models.StudentProgress.user_id == student.id,
                db_models.StudentProgress.module_id.in_([m.id for m in course.modules]),
                db_models.StudentProgress.status == 'completed'
            ).count()
            progress = round((completed_modules / total_modules) * 100) if total_modules > 0 else 0

            student_data["enrollments"].append({
                "course_title": course.title,
                "room_name": room.name if room else "Sin Sala (Libre)",
                "progress": progress
            })

        report.append(student_data)

    return report


def get_all_rooms_summary(db: Session):
    """
    Obtiene un resumen de todas las salas, incluyendo su instructor,
    cantidad de cursos y cantidad de miembros.
    """
    rooms = db.query(db_models.Room).options(
        joinedload(db_models.Room.instructor).joinedload(db_models.User.profile)
    ).all()

    summary = []
    for room in rooms:
        # --- CORRECCIÓN: Maneja el caso de que el perfil o instructor sea None ---
        instructor_name = "Sin Asignar"
        if room.instructor:
            instructor_name = (
                room.instructor.profile.first_name if room.instructor.profile else room.instructor.username)

        summary.append({
            "id": room.id,
            "name": room.name,
            "instructor_name": instructor_name,
            "course_count": len(room.courses),
            "member_count": len(room.members)
        })
    return summary
