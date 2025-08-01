# backend/app/services/module_service.py

from sqlalchemy.orm import Session
from app.repositories import module_repo, quiz_repo
from app.services import ai_service
from app import db_models

class ModuleService:
    def __init__(self, db: Session):
        self.db = db

    async def generate_and_save_content(self, module_id: int) -> db_models.Module | None:
        """
        Orquesta la generación de contenido y el quiz para un módulo.
        """
        module = module_repo.get_module_by_id(self.db, module_id)
        if not module:
            return None

        # --- LÍNEAS DE DIAGNÓSTICO ---
        print(f"--- Iniciando generación para Módulo ID: {module_id} ---")
        print(f"Título enviado a la IA: '{module.title}'")
        # -----------------------------

        # 1. Genera y guarda el contenido de la lección
        generated_content = ai_service.generate_module_content_from_ai(
            module.title, module.description
        )
        updated_module = module_repo.update_module_content(
            self.db, module_id, generated_content
        )

        # 2. Genera y guarda el quiz asociado
        quiz_data = ai_service.generate_quiz_from_ai(module.title, module.description)
        if quiz_data and quiz_data.get("questions"):
            quiz_repo.create_quiz_for_module(self.db, module_id, quiz_data["questions"])

        return updated_module