from sqlalchemy.orm import Session
from app import db_models


def create_default_subscription(db: Session, user_id: int, role_name: str):
    """
    Crea una suscripción gratuita por defecto para un nuevo usuario.
    """
    plan_name = "Instructor Básico" if role_name == 'instructor' else "Estudiante Básico"

    db_subscription = db_models.Subscription(
        user_id=user_id,
        plan_name=plan_name
    )
    db.add(db_subscription)
    # No hacemos db.commit() aquí, se hará en la función que lo llama.