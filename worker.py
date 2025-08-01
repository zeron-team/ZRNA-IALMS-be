# worker.py
from celery import Celery

celery_app = Celery("tasks", broker="redis://localhost:6379/0", backend="redis://localhost:6379/0")

@celery_app.task
def generate_full_course_content(course_id):
    # Aquí va toda la lógica pesada:
    # 1. Llamar a la IA para generar la currícula
    # 2. Guardar los módulos
    # 3. Para cada módulo, llamar a la IA para generar contenido
    # 4. Para cada módulo, llamar a la IA para generar quizzes
    # 5. Actualizar el estado del curso en la DB a 'listo'
    print(f"Curso {course_id} generado completamente.")