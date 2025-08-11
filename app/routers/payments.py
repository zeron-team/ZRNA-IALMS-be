# backend/app/routers/payments.py

import mercadopago
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.dependencies import get_db
from app.security import get_current_active_user
from app.models.user import User as UserSchema
from app.config import MERCADOPAGO_ACCESS_TOKEN, FRONTEND_URL

router = APIRouter(prefix="/payments", tags=["Payments"])


@router.post("/create-preference/{plan_id}")
def create_payment_preference(
        plan_id: str,
        db: Session = Depends(get_db),
        current_user: UserSchema = Depends(get_current_active_user)
):
    # ... (lógica para obtener el precio del plan)

    sdk = mercadopago.SDK(MERCADOPAGO_ACCESS_TOKEN)

    preference_data = {
        "items": [
            {"title": plan["title"], "quantity": 1, "unit_price": plan["price"]}
        ],
        "back_urls": {
            "success": f"{FRONTEND_URL}/payment-status?status=success",
            "failure": f"{FRONTEND_URL}/payment-status?status=failure",
            "pending": f"{FRONTEND_URL}/payment-status?status=pending"
        },
        "auto_return": "approved",
        "external_reference": f"user_{current_user.id}_plan_{plan_id}",
        "notification_url": "https://TU_DOMINIO/api/payments/webhook"  # Debes configurar esto en producción
    }

    preference_response = sdk.preference().create(preference_data)
    preference = preference_response["response"]
    return {"checkout_url": preference["init_point"]}


@router.post("/webhook")
async def handle_mercado_pago_webhook(request: Request, db: Session = Depends(get_db)):
    """Recibe y procesa notificaciones de pago de Mercado Pago."""
    data = await request.json()
    if data.get("type") == "payment":
        payment_id = data.get("data", {}).get("id")
        # Aquí iría la lógica para verificar el pago y actualizar el rol del usuario
        print(f"Recibida notificación de pago: {payment_id}")
    return {"status": "ok"}