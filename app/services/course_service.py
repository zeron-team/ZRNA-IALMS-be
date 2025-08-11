# backend/app/services/course_service.py

from sqlalchemy.orm import Session
from app.repositories import course_repo, progress_repo, quiz_repo
from app.models import course as course_schemas
from app.services import ai_service


class CourseService:
    def __init__(self, db: Session):
        self.db = db

    async def find_one_with_progress(self, course_id: int, user_id: int):
        # ... (lógica existente)
        pass

    async def create_new_course(self, course: course_schemas.CourseCreate, instructor_id: int):
        return course_repo.create_course(self.db, course, instructor_id)

    async def generate_and_save_curriculum(self, course_id: int):
        """
        Genera la currícula para un curso, y luego genera un quiz para cada
        nuevo módulo creado.
        """
        db_course = course_repo.get_course_by_id(self.db, course_id)
        if not db_course:
            return None

        # Paso 1: Genera y guarda los módulos
        print(f"--- [Paso 1] Obteniendo currícula de la IA para el curso: '{db_course.title}' ---")
        curriculum_data = ai_service.generate_curriculum_from_ai(db_course.title, db_course.description)
        modules_data = curriculum_data.get("modules", [])

        if not modules_data:
            print("!!! La IA no devolvió módulos. Abortando.")
            return []

        course_repo.add_modules_to_course(self.db, course_id, modules_data)
        updated_course = course_repo.get_course_by_id(self.db, course_id)

        # Paso 2: Itera sobre cada nuevo módulo para crear su quiz
        print(f"--- [Paso 2] Iniciando generación de quizzes para {len(updated_course.modules)} módulos ---")
        for module in updated_course.modules:
            print(f"Generando quiz para el módulo: '{module.title}' (ID: {module.id})")
            quiz_content = ai_service.generate_quiz_from_ai(module.title, module.description)
            if quiz_content and quiz_content.get("questions"):
                quiz_repo.create_quiz_for_module(self.db, module.id, quiz_content["questions"])
                print(f"-> Quiz para '{module.title}' creado con éxito.")
            else:
                print(f"-> !!! No se pudo generar quiz para '{module.title}'.")

        return updated_course.modules

    # --- El resto de tus funciones de servicio ---
    async def find_all(self):
        return course_repo.get_all_courses(self.db)

    async def mark_module_completed(self, user_id: int, module_id: int):
        return progress_repo.mark_module_as_completed(self.db, user_id, module_id)

    async def find_courses_by_instructor(self, instructor_id: int):
        return course_repo.get_courses_by_instructor_id(self.db, instructor_id)

    async def update_existing_course(self, course_id: int, course_update: course_schemas.CourseCreate, user_id: int):
        return course_repo.update_course(self.db, course_id, course_update, user_id)

    async def delete_existing_course(self, course_id: int, user_id: int):
        return course_repo.delete_course(self.db, course_id, user_id)