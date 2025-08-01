from sqlalchemy.orm import Session
from app.repositories import course_repo, progress_repo
from app.models import course as course_schemas
from app.services import ai_service


class CourseService:
    def __init__(self, db: Session):
        self.db = db

    async def find_all(self):
        return course_repo.get_all_courses(self.db)

    async def find_one_with_progress(self, course_id: int, user_id: int):
        db_course = course_repo.get_course_by_id(self.db, course_id)
        if not db_course:
            return None

        user_progress_query = progress_repo.get_progress_for_course(self.db, user_id, course_id)
        user_progress_map = {p.module_id: p.status for p in user_progress_query}

        modules_with_status = [
            course_schemas.Module(
                id=module.id,
                title=module.title,
                description=module.description,
                order_index=module.order_index,
                status=user_progress_map.get(module.id, 'not_started')
            ) for module in sorted(db_course.modules, key=lambda m: m.order_index)
        ]

        return course_schemas.CourseDetail(
            id=db_course.id,
            title=db_course.title,
            description=db_course.description,
            modules=modules_with_status
        )

    async def create_new_course(self, course: course_schemas.CourseCreate, instructor_id: int):
        # Llama a la función del repositorio, pasando el instructor_id
        return course_repo.create_course(self.db, course, instructor_id)

    # --- ESTA ES LA FUNCIÓN QUE FALTA AHORA ---
    async def generate_and_save_curriculum(self, course_id: int):
        db_course = course_repo.get_course_by_id(self.db, course_id)
        if not db_course:
            return None

        curriculum_data = ai_service.generate_curriculum_from_ai(db_course.title, db_course.description)
        modules = curriculum_data.get("modules", [])
        if not modules:
            return []

        course_repo.add_modules_to_course(self.db, course_id, modules)
        updated_course = course_repo.get_course_by_id(self.db, course_id)
        return updated_course.modules

    # ----------------------------------------------

    async def mark_module_completed(self, user_id: int, module_id: int):
        return progress_repo.mark_module_as_completed(self.db, user_id, module_id)

    async def find_courses_by_instructor(self, instructor_id: int):
        return course_repo.get_courses_by_instructor_id(self.db, instructor_id)

    async def update_existing_course(self, course_id: int, course_update: course_schemas.CourseCreate, user_id: int):
        return course_repo.update_course(self.db, course_id, course_update, user_id)

    async def delete_existing_course(self, course_id: int, user_id: int):
        return course_repo.delete_course(self.db, course_id, user_id)