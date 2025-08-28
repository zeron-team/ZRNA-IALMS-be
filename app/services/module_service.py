# backend/app/services/module_service.py

from sqlalchemy.orm import Session
from app.repositories import module_repo, quiz_repo
from app.services import ai_service
from app import db_models
from typing import Optional

class ModuleService:
    def __init__(self, db: Session):
        self.db = db

    async def generate_and_save_content(self, module_id: int) -> Optional[db_models.Module]:
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
            print(f"-> Quiz para '{module.title}' creado con éxito.")
        else:
            print(f"-> !!! No se pudo generar quiz para '{module.title}'.")


        return updated_module

    async def generate_and_save_audio(self, module_id: int) -> Optional[db_models.Module]:
        """
        Genera y guarda el audio para un módulo.
        """
        module = module_repo.get_module_by_id(self.db, module_id)
        if not module or not module.content_data:
            return None

        audio_path = ai_service.generate_audio_from_text(module.content_data, module_id)
        if audio_path:
            updated_module = module_repo.update_module_audio(self.db, module_id, audio_path)
            print(f"-> Audio para '{module.title}' creado con éxito.")
            return updated_module
        else:
            print(f"-> !!! No se pudo generar audio para '{module.title}'.")
            return None