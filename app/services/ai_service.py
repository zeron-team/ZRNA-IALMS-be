# backend/app/services/ai_service.py

import google.generativeai as genai
import json
from sqlalchemy.orm import Session
from typing import List
from app import db_models
from app.repositories import course_repo
from app.config import GOOGLE_API_KEY

# Configura la API key de forma segura al iniciar el servicio
try:
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    print(f"Error fatal al configurar la API de Google: {e}")
    model = None


def generate_student_alert(student_name: str, course_title: str, progress_percentage: int) -> str:
    """
    Genera un mensaje personalizado para un estudiante usando Gemini AI.
    """
    progress_percentage = max(0, min(100, int(progress_percentage)))
    prompt_context = "Actúa como un tutor académico."

    if progress_percentage >= 80:
        prompt = f"""{prompt_context} Redacta un mensaje corto y positivo para '{student_name}', que ha completado un {progress_percentage}% del curso '{course_title}'. Anímale a dar el último esfuerzo."""
    else:
        prompt = f"""{prompt_context} Redacta un mensaje corto y de apoyo para '{student_name}', que tiene un {progress_percentage}% de progreso en el curso '{course_title}'. Anímale a continuar sin presionarle."""

    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Error en la llamada a la API de Gemini: {e}")
        return "Hubo un problema al generar el consejo de la IA. Por favor, inténtalo más tarde."


def generate_curriculum_from_ai(course_title: str, course_description: str) -> dict:
    """
    Usa Gemini para generar una currícula de curso en formato JSON.
    """
    if not model: return {"modules": []}
    prompt = f"""
    Actúa como un diseñador instruccional experto. Basado en el título y descripción de un curso, genera una currícula detallada.
    Título: "{course_title}"
    Descripción: "{course_description}"

    Tu respuesta DEBE ser un objeto JSON válido y nada más, sin texto introductorio ni explicaciones adicionales. El objeto debe tener una clave "modules" que sea un array de objetos.
    Cada objeto debe tener las claves: "title" (string), "description" (string), y "order_index" (integer, comenzando en 1).
    Genera entre 15 y 20 módulos.
    """

    try:
        response = model.generate_content(prompt)
        # Limpia la respuesta para asegurar que sea solo JSON
        cleaned_response = response.text.strip().replace("```json", "").replace("```", "")
        return json.loads(cleaned_response)
    except (json.JSONDecodeError, Exception) as e:
        print(f"Error al generar o parsear la currícula de la IA: {e}")
        return {"modules": []}  # Devuelve una estructura vacía en caso de error


def generate_quiz_from_ai(module_title: str, module_description: str) -> dict:
    """Usa Gemini para generar un quiz para un módulo en formato JSON."""
    if not model: return {"questions": []}
    prompt = f"""
    Actúa como un experto en evaluación educativa. Para un módulo con el título "{module_title}" y descripción "{module_description}", crea un mini-quiz.
    Tu respuesta DEBE ser un objeto JSON válido y nada más, con una clave "questions" que sea un array.
    Cada pregunta debe tener "question_text" y un array "options" con 4 objetos.
    Cada opción debe tener "option_text" y "is_correct" (boolean, solo una true).
    Genera 5 preguntas.
    """
    try:
        response = model.generate_content(prompt)
        cleaned_response = response.text.strip().replace("```json", "").replace("```", "")
        return json.loads(cleaned_response)
    except Exception as e:
        print(f"Error al generar quiz de IA: {e}")
        return {"questions": []}


def generate_module_content_from_ai(module_title: str, module_description: str) -> str:
    """Usa Gemini para generar el contenido de una lección en formato Markdown."""
    prompt = f"""
    Actúa como un educador experto en tecnología. Escribe el contenido completo para una lección de un curso.

    Título del Módulo: "{module_title}"
    Resumen del Módulo: "{module_description}"

    Tu respuesta DEBE ser texto en formato Markdown y nada más. Estructura el contenido de forma clara:
    - Empieza con una breve introducción.
    - Usa encabezados (##) para las secciones principales.
    - Usa listas con viñetas o numeradas para explicar conceptos clave.
    - Incluye ejemplos de código en bloques de código (```python ... ```) si es relevante.
    - Termina con un párrafo de resumen.

    No incluyas el título principal del módulo en tu respuesta, solo el contenido de la lección.
    """
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Error al generar el contenido del módulo: {e}")
        return "Error al generar contenido."


def generate_course_summary_from_ai(title: str, description: str) -> str:
    """Genera un resumen de objetivos del curso en formato Markdown."""
    prompt = f"""
    Actúa como un asesor académico. Para un curso con el siguiente título y descripción, redacta un resumen atractivo y conciso.

    Título: "{title}"
    Descripción: "{description}"

    Tu respuesta DEBE ser texto en formato Markdown. Estructura el resumen así:
    - Un encabezado "### ¿Qué aprenderás en este curso?".
    - Una lista con viñetas de 7 a 10 objetivos de aprendizaje clave que el alumno logrará.
    - Un encabezado "### ¿A quién está dirigido?".
    - Un párrafo corto describiendo el perfil del estudiante ideal.
    """
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Error al generar el resumen: {e}"


def suggest_missing_courses_for_path(path_title: str, existing_courses: List[str]) -> List[str]:
    """
    Dada una carrera y los cursos que ya tiene, la IA sugiere los que faltan.
    """
    courses_list = ", ".join(existing_courses)
    prompt = f"""
    Actúa como un experto diseñador de currículas académicas para una plataforma de e-learning de tecnología.
    La ruta de conocimiento es: "{path_title}".
    Los cursos que ya existen en esta ruta son: {courses_list}.

    Analiza la ruta y los cursos existentes. Sugiere una lista de 3 a 5 títulos de cursos adicionales que complementarían y completarían esta ruta de conocimiento de forma lógica.

    Tu respuesta DEBE ser un objeto JSON válido y nada más. El objeto debe tener una clave "suggested_courses" que sea un array de strings, donde cada string es el título de un curso sugerido.
    Ejemplo de formato de respuesta:
    {{
      "suggested_courses": [
        "Estadística Descriptiva con Python",
        "Machine Learning: Modelos de Regresión"
      ]
    }}
    """
    try:
        response = model.generate_content(prompt)
        cleaned_response = response.text.strip().replace("```json", "").replace("```", "")
        data = json.loads(cleaned_response)
        return data.get("suggested_courses", [])
    except Exception as e:
        print(f"Error al sugerir cursos: {e}")
        return []


def get_course_recommendations(db: Session, enrolled_titles: List[str]) -> List[db_models.Course]:
    """
    Basado en los cursos de un alumno, la IA recomienda otros cursos de la plataforma.
    """
    # Obtenemos todos los cursos disponibles que no está tomando el alumno
    all_courses = course_repo.get_all_courses(db)
    available_courses = [c for c in all_courses if c.title not in enrolled_titles]
    available_titles = [c.title for c in available_courses]

    if not available_courses:
        return []

    prompt = f"""
    Actúa como un orientador académico en una plataforma de e-learning de tecnología.
    Un estudiante está actualmente inscrito en los siguientes cursos: {', '.join(enrolled_titles)}.
    La lista de otros cursos disponibles en la plataforma es: {', '.join(available_titles)}.

    Basado en sus intereses actuales, recomienda 2 o 3 cursos de la lista de disponibles que serían el siguiente paso lógico en su aprendizaje.

    Tu respuesta DEBE ser un objeto JSON válido y nada más, con una clave "recommendations" que sea un array de strings con los títulos exactos de los cursos que recomiendas.
    Ejemplo:
    {{
      "recommendations": ["Docker", "Introducción a la IA con Gemini"]
    }}
    """
    try:
        response = model.generate_content(prompt)
        cleaned_response = response.text.strip().replace("```json", "").replace("```", "")
        data = json.loads(cleaned_response)
        recommended_titles = data.get("recommendations", [])

        # Devolvemos los objetos de curso completos de los cursos recomendados
        return [c for c in available_courses if c.title in recommended_titles]
    except Exception as e:
        print(f"Error al generar recomendaciones: {e}")
        return []


def generate_motivational_phrase(score: int, passed: bool) -> str:
    """Genera una frase motivadora basada en el resultado del quiz."""
    if passed:
        prompt = f"Actúa como un tutor motivador. Escribe una frase corta (máximo 20 palabras) felicitando a un estudiante por aprobar un quiz con un {score}%."
    else:
        prompt = f"Actúa como un tutor comprensivo. Escribe una frase corta (máximo 20 palabras) animando a un estudiante que no aprobó un quiz con un {score}%, motivándolo a repasar y volver a intentarlo."

    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception:
        return "¡Sigue esforzándote!"