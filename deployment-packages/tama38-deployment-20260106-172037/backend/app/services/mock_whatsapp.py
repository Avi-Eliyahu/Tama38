"""
Mock WhatsApp Service - Simulates Twilio WhatsApp API
"""
from sqlalchemy.orm import Session
from datetime import datetime
from app.models.owner import Owner
from app.models.document import DocumentSignature
import uuid
import logging

logger = logging.getLogger(__name__)


class MockWhatsAppService:
    """Mock WhatsApp service for Phase 1 development"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def send_message(self, owner_id: str, message_body: str, message_type: str = "TEXT") -> dict:
        """Send a WhatsApp message (stores in database, doesn't actually send)"""
        owner = self.db.query(Owner).filter(Owner.owner_id == owner_id).first()
        if not owner:
            raise ValueError("Owner not found")
        
        # In Phase 1, we store messages in a mock table
        # For now, just log it
        message_id = str(uuid.uuid4())
        
        logger.info(
            "Mock WhatsApp message sent",
            extra={
                "message_id": message_id,
                "owner_id": owner_id,
                "message_type": message_type,
                "to": owner.phone_for_contact,
            }
        )
        
        return {
            "message_id": message_id,
            "status": "QUEUED",
            "to": owner.phone_for_contact,
            "body": message_body,
        }
    
    def send_template(self, owner_id: str, template_name: str, variables: dict) -> dict:
        """Send a WhatsApp template message"""
        # In Phase 1, render template and send as regular message
        # Template rendering would happen here
        message_body = f"Template: {template_name} with variables: {variables}"
        return self.send_message(owner_id, message_body, "TEMPLATE")
    
    def simulate_incoming_message(self, from_number: str, body: str) -> dict:
        """Simulate an incoming WhatsApp message (for testing)"""
        # Find owner by phone
        owner = self.db.query(Owner).filter(
            Owner.phone_for_contact.ilike(f"%{from_number}%")
        ).first()
        
        if not owner:
            return {"error": "Owner not found for this phone number"}
        
        # Process message based on body
        response_body = "Thank you for your message. This is a mock response."
        
        if "status" in body.lower():
            # Return building status
            from app.models.unit import Unit
            from app.models.building import Building
            unit = self.db.query(Unit).filter(Unit.unit_id == owner.unit_id).first()
            if unit:
                building = self.db.query(Building).filter(Building.building_id == unit.building_id).first()
                if building:
                    response_body = f"Building {building.building_name}: {building.signature_percentage}% signatures"
        
        logger.info(
            "Mock WhatsApp incoming message simulated",
            extra={
                "from": from_number,
                "owner_id": str(owner.owner_id),
                "body": body,
            }
        )
        
        return {
            "message_id": str(uuid.uuid4()),
            "from": from_number,
            "body": response_body,
            "status": "DELIVERED",
        }

