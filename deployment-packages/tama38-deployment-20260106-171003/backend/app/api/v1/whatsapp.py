"""
Mock WhatsApp API endpoints
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from uuid import UUID
from app.core.database import get_db
from app.models.user import User
from app.api.dependencies import get_current_user
from app.services.mock_whatsapp import MockWhatsAppService
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/whatsapp", tags=["whatsapp"])


class WhatsAppSend(BaseModel):
    owner_id: str
    message_body: str
    message_type: str = "TEXT"


class WhatsAppWebhook(BaseModel):
    From: str
    Body: str
    MessageSid: str


@router.post("/mock/send")
async def send_whatsapp_message(
    message_data: WhatsAppSend,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Send a mock WhatsApp message"""
    service = MockWhatsAppService(db)
    try:
        result = service.send_message(
            message_data.owner_id,
            message_data.message_body,
            message_data.message_type
        )
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.post("/mock/webhook")
async def simulate_whatsapp_webhook(
    webhook_data: WhatsAppWebhook,
    db: Session = Depends(get_db)
):
    """Simulate incoming WhatsApp webhook (for testing)"""
    service = MockWhatsAppService(db)
    result = service.simulate_incoming_message(webhook_data.From, webhook_data.Body)
    
    if "error" in result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=result["error"]
        )
    
    return result


@router.get("/conversations")
async def get_conversations(
    owner_id: Optional[UUID] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get WhatsApp conversation history (mock data in Phase 1)"""
    # In Phase 1, return mock conversation data
    # In Phase 2, this would query whatsapp_messages table
    return {
        "conversations": [],
        "message": "Mock WhatsApp conversations - Phase 1",
    }

