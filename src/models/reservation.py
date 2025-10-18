"""
Reservation data model for the MCP server.
"""
from datetime import date
from typing import Optional
from pydantic import BaseModel, Field, validator


class Reservation(BaseModel):
    """Hotel reservation model."""
    id: str = Field(description="Unique reservation identifier")
    guest_name: str = Field(description="Name of the guest")
    room_type: str = Field(description="Type of room reserved")
    check_in_date: date = Field(description="Check-in date")
    check_out_date: date = Field(description="Check-out date")
    total_price: float = Field(ge=0, description="Total price must be non-negative")

    @validator('check_out_date')
    def validate_checkout_after_checkin(cls, v: date, values: dict) -> date:
        """Ensure check-out date is after check-in date."""
        if 'check_in_date' in values and v <= values['check_in_date']:
            raise ValueError('Check-out date must be after check-in date')
        return v

    @validator('id')
    def validate_id_not_empty(cls, v: str) -> str:
        """Ensure ID is not empty."""
        if not v.strip():
            raise ValueError('Reservation ID cannot be empty')
        return v.strip()

    @validator('guest_name')
    def validate_guest_name_not_empty(cls, v: str) -> str:
        """Ensure guest name is not empty."""
        if not v.strip():
            raise ValueError('Guest name cannot be empty')
        return v.strip()

    @validator('room_type')
    def validate_room_type_not_empty(cls, v: str) -> str:
        """Ensure room type is not empty."""
        if not v.strip():
            raise ValueError('Room type cannot be empty')
        return v.strip()

    class Config:
        """Pydantic configuration."""
        json_encoders = {
            date: lambda v: v.isoformat()
        }
        json_schema_extra = {
            "example": {
                "id": "R123",
                "guest_name": "John Doe",
                "room_type": "Deluxe",
                "check_in_date": "2025-07-20",
                "check_out_date": "2025-07-23",
                "total_price": 500.00
            }
        } 