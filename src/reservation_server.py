"""
FastMCP reservation server with integrated tools.
"""
import sys
import argparse
import os
from datetime import date
from pathlib import Path
from typing import List, Optional
from pydantic import Field
from mcp.server.fastmcp import FastMCP
import json

from .models.reservation import Reservation
from .storage.json_storage import JSONStorage

# Create FastMCP server
mcp = FastMCP("reservation-server")

# Global storage instance
storage = None


def get_storage() -> JSONStorage:
    """Get the global storage instance."""
    global storage
    if storage is None:
        raise RuntimeError("Storage not initialized")
    return storage


@mcp.tool()
def create_reservation(
    id: str = Field(description="Unique reservation ID"),
    guest_name: str = Field(description="Name of the guest"),
    room_type: str = Field(description="Type of room (e.g., single, double, suite)"),
    check_in_date: str = Field(description="Check-in date in YYYY-MM-DD format"),
    check_out_date: str = Field(description="Check-out date in YYYY-MM-DD format"),
    total_price: float = Field(description="Total price of the reservation")
) -> str:
    """Create a new hotel reservation."""
    try:
        storage = get_storage()
        
        # Convert date strings to date objects
        check_in_date_obj = date.fromisoformat(check_in_date)
        check_out_date_obj = date.fromisoformat(check_out_date)
        
        # Create reservation object
        reservation = Reservation(
            id=id,
            guest_name=guest_name,
            room_type=room_type,
            check_in_date=check_in_date_obj,
            check_out_date=check_out_date_obj,
            total_price=total_price
        )
        
        # Save to storage
        created_reservation = storage.create_reservation(reservation)
        
        return f"Successfully created reservation: {created_reservation.model_dump_json(indent=2)}"
        
    except ValueError as e:
        return f"Validation error: {str(e)}"
    except Exception as e:
        return f"Error creating reservation: {str(e)}"


@mcp.tool()
def get_reservation(
    id: str = Field(description="Reservation ID to retrieve")
) -> str:
    """Get a reservation by ID."""
    try:
        storage = get_storage()
        
        reservation = storage.get_reservation(id)
        
        if reservation is None:
            return f"Reservation with ID '{id}' not found"
        
        return f"Reservation found: {reservation.model_dump_json(indent=2)}"
        
    except Exception as e:
        return f"Error retrieving reservation: {str(e)}"


@mcp.tool()
def update_reservation(
    id: str = Field(description="Reservation ID to update"),
    guest_name: Optional[str] = Field(default=None, description="Updated guest name"),
    room_type: Optional[str] = Field(default=None, description="Updated room type"),
    check_in_date: Optional[str] = Field(default=None, description="Updated check-in date in YYYY-MM-DD format"),
    check_out_date: Optional[str] = Field(default=None, description="Updated check-out date in YYYY-MM-DD format"),
    total_price: Optional[float] = Field(default=None, description="Updated total price")
) -> str:
    """Update an existing reservation."""
    try:
        storage = get_storage()
        
        # Check if reservation exists
        existing_reservation = storage.get_reservation(id)
        if existing_reservation is None:
            return f"Reservation with ID '{id}' not found"
        
        # Update fields with provided values or keep existing ones
        updated_guest_name = guest_name if guest_name is not None else existing_reservation.guest_name
        updated_room_type = room_type if room_type is not None else existing_reservation.room_type
        updated_check_in_date = existing_reservation.check_in_date
        updated_check_out_date = existing_reservation.check_out_date
        updated_total_price = total_price if total_price is not None else existing_reservation.total_price
        
        # Convert date strings to date objects if provided
        if check_in_date is not None:
            updated_check_in_date = date.fromisoformat(check_in_date)
        if check_out_date is not None:
            updated_check_out_date = date.fromisoformat(check_out_date)
        
        # Create updated reservation
        updated_reservation = Reservation(
            id=id,
            guest_name=updated_guest_name,
            room_type=updated_room_type,
            check_in_date=updated_check_in_date,
            check_out_date=updated_check_out_date,
            total_price=updated_total_price
        )
        
        # Update in storage
        result = storage.update_reservation(id, updated_reservation)
        
        if result is None:
            return f"Failed to update reservation with ID '{id}'"
        
        return f"Successfully updated reservation: {result.model_dump_json(indent=2)}"
        
    except ValueError as e:
        return f"Validation error: {str(e)}"
    except Exception as e:
        return f"Error updating reservation: {str(e)}"


@mcp.tool()
def delete_reservation(
    id: str = Field(description="Reservation ID to delete")
) -> str:
    """Delete a reservation by ID."""
    try:
        storage = get_storage()
        
        success = storage.delete_reservation(id)
        
        if not success:
            return f"Reservation with ID '{id}' not found"
        
        return f"Successfully deleted reservation with ID '{id}'"
        
    except Exception as e:
        return f"Error deleting reservation: {str(e)}"


@mcp.tool()
def list_reservations() -> str:
    """List all reservations."""
    try:
        storage = get_storage()
        
        reservations = storage.list_reservations()
        
        if not reservations:
            return "No reservations found"
        
        reservations_text = "All reservations:\n\n"
        for reservation in reservations:
            reservations_text += f"{reservation.model_dump_json(indent=2)}\n\n"
        
        return reservations_text.strip()
        
    except Exception as e:
        return f"Error listing reservations: {str(e)}"

@mcp.tool()
def create_service(
    id: str = Field(description="Unique service ID"),
    name: str = Field(description="Service name (e.g., Breakfast)"),
    description: Optional[str] = Field(default="", description="Service description"),
    price: float = Field(description="Service price"),
    category: Optional[str] = Field(default="", description="Service category (e.g., dining, parking)"),
    reservation_id: Optional[str] = Field(default=None, description="Reservation ID to attach this service to")
) -> str:
    """Create a new service and optionally attach it to a reservation."""
    try:
        storage = get_storage()

        # If a reservation_id was provided, ensure reservation exists
        if reservation_id:
            if not storage.reservation_exists(reservation_id):
                return f"Reservation with ID '{reservation_id}' not found - cannot attach service"

        service = {
            "id": id,
            "name": name,
            "description": description or "",
            "price": price,
            "category": category or "",
            "reservation_id": reservation_id
        }

        created = storage.create_service(service)
        return f"Successfully created service: {json.dumps(created, indent=2)}"
    except ValueError as e:
        return f"Validation error: {str(e)}"
    except Exception as e:
        return f"Error creating service: {str(e)}"


@mcp.tool()
def list_services() -> str:
    """List all services."""
    try:
        storage = get_storage()
        services = storage.list_services()
        if not services:
            return "No services found"
        text = "All services:\n\n"
        for s in services:
            text += json.dumps(s, indent=2) + "\n\n"
        return text.strip()
    except Exception as e:
        return f"Error listing services: {str(e)}"


@mcp.tool()
def get_services_for_reservation(
    reservation_id: str = Field(description="Reservation ID to list services for")
) -> str:
    """Get services attached to a reservation."""
    try:
        storage = get_storage()
        if not storage.reservation_exists(reservation_id):
            return f"Reservation with ID '{reservation_id}' not found"
        services = storage.get_services_by_reservation(reservation_id)
        if not services:
            return f"No services found for reservation '{reservation_id}'"
        return f"Services for reservation {reservation_id}:\n\n" + "\n\n".join(json.dumps(s, indent=2) for s in services)
    except Exception as e:
        return f"Error retrieving services: {str(e)}"
    
def main() -> None:
    """Main entry point for the FastMCP server."""
    global storage
    
    parser = argparse.ArgumentParser(description="FastMCP Reservation Server")
    parser.add_argument(
        "directory",
        help="Directory path where reservations.json will be stored"
    )
    
    args = parser.parse_args()
    
    # Validate directory path
    directory_path = Path(args.directory)
    if not directory_path.exists():
        print(f"Error: Directory '{args.directory}' does not exist", file=sys.stderr)
        sys.exit(1)
    
    if not directory_path.is_dir():
        print(f"Error: '{args.directory}' is not a directory", file=sys.stderr)
        sys.exit(1)
    
    # Initialize storage
    storage = JSONStorage(str(directory_path))
    
    # Start the server (tools are already registered via decorators)
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main() 