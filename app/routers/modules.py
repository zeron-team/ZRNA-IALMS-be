# backend/app/routers/modules.py

# --- FastAPI & SQLAlchemy ---
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse # Import StreamingResponse
from sqlalchemy.orm import Session
import markdown # Import markdown
from weasyprint import HTML # Import HTML from WeasyPrint
import io # Import io

# --- Modelos Pydantic ---
from app.models.module import ModuleResponse as ModuleSchema
from app.models.user import User as UserSchema

# --- Dependencias, Repositorios y Servicios ---
from app.dependencies import get_db, get_module_service
from app.repositories import module_repo, enrollment_repo
from app.services.module_service import ModuleService
from app.security import instructor_required, get_current_active_user, can_edit_module, is_enrolled_in_course_from_module

router = APIRouter(
    prefix="/modules",
    tags=["Modules"]
)

@router.get("/{module_id}", response_model=ModuleSchema)
def read_module(
    module_id: int,
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_active_user)
):
    db_module = module_repo.get_module_by_id(db, module_id=module_id)
    if db_module is None:
        raise HTTPException(status_code=404, detail="Módulo no encontrado")

    db_course = db_module.course

    # --- LÓGICA DE PERMISOS CORREGIDA ---
    is_enrolled = enrollment_repo.is_enrolled(db, user_id=current_user.id, course_id=db_course.id)
    is_instructor_or_admin = current_user.role.name in ['instructor', 'admin']
    is_creator = db_course.creator_id == current_user.id

    # Permite el acceso si se cumple CUALQUIERA de estas condiciones
    if not is_enrolled and not is_instructor_or_admin and not is_creator:
        raise HTTPException(status_code=403, detail="No tienes permiso para ver este módulo.")
    # ------------------------------------------

    return db_module

@router.post("/{module_id}/generate-content", response_model=ModuleSchema)
async def generate_content_for_module(
    module_id: int,
    service: ModuleService = Depends(get_module_service),
    # Reemplaza 'instructor_required' con la nueva dependencia
    current_user: UserSchema = Depends(is_enrolled_in_course_from_module)
):
    """Genera y guarda el contenido detallado para un módulo usando IA."""
    updated_module = await service.generate_and_save_content(module_id)
    if not updated_module:
        raise HTTPException(status_code=500, detail="Failed to generate content")
    return updated_module

@router.post("/{module_id}/generate-audio", response_model=ModuleSchema)
async def generate_audio_for_module(
    module_id: int,
    service: ModuleService = Depends(get_module_service),
    current_user: UserSchema = Depends(get_current_active_user)
):
    """Genera y guarda el audio para un módulo usando IA."""
    updated_module = await service.generate_and_save_audio(module_id)
    if not updated_module:
        raise HTTPException(status_code=500, detail="Failed to generate audio")
    return updated_module

@router.get("/{module_id}/download-pdf", response_class=StreamingResponse)
async def download_module_pdf(
    module_id: int,
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_active_user)
):
    db_module = module_repo.get_module_by_id(db, module_id=module_id)
    if db_module is None:
        raise HTTPException(status_code=404, detail="Módulo no encontrado")

    db_course = db_module.course

    # Permission check (similar to read_module)
    is_enrolled = enrollment_repo.is_enrolled(db, user_id=current_user.id, course_id=db_course.id)
    is_instructor_or_admin = current_user.role.name in ['instructor', 'admin']
    is_creator = db_course.creator_id == current_user.id

    if not is_enrolled and not is_instructor_or_admin and not is_creator:
        raise HTTPException(status_code=403, detail="No tienes permiso para descargar este módulo.")

    if not db_module.content_data:
        raise HTTPException(status_code=404, detail="Contenido del módulo no disponible para descargar.")

    # Convert Markdown to HTML
    html_content = markdown.markdown(db_module.content_data)

    # Basic HTML template for PDF
    html_template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>{db_module.title}</title>
        <style>
            @page {{
                @bottom-center {{
                    content: "www.zeronacademy.com";
                    color: #888;
                    font-size: 10px;
                }}
            }}
            body {{ font-family: sans-serif; margin: 20mm; }}
            h1 {{ color: #333; }}
            pre {{ background-color: #eee; padding: 10px; border-radius: 5px; overflow-x: auto; }}
            .watermark {{
                position: fixed;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%) rotate(-45deg);
                color: rgba(0, 0, 0, 0.08);
                font-size: 72px;
                font-weight: bold;
                white-space: nowrap;
                z-index: 1000;
                pointer-events: none;
            }}
        </style>
    </head>
    <body>
        <div class="watermark">www.zeronacademy.com</div>
        <h1>{db_module.title}</h1>
        <p><strong>Descripción:</strong> {db_module.description}</p>
        <hr/>
        {html_content}
    </body>
    </html>
    """

    # Generate PDF
    pdf_file = io.BytesIO()
    HTML(string=html_template).write_pdf(pdf_file)
    pdf_file.seek(0)

    return StreamingResponse(
        pdf_file,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=\"{db_module.title}.pdf\""}
    )
