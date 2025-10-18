"""
JSON file storage implementation for reservations.
"""
import json
import os
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import date

from ..models.reservation import Reservation


class JSONStorage:
    """JSON file-based storage for reservations."""
    
    def __init__(self, directory_path: str):
        """Initialize storage with directory path."""
        self.directory_path = Path(directory_path)
        self.file_path = self.directory_path / "reservations.json"
        self.services_path = self.directory_path / "services.json"
        
        # Ensure directory exists
        self.directory_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize file if it doesn't exist
        if not self.file_path.exists():
            self._write_reservations([])
        if not self.services_path.exists():
            self._write_services([])
    
    def _read_reservations(self) -> List[Dict[str, Any]]:
        """Read reservations from JSON file."""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
        except (json.JSONDecodeError, FileNotFoundError):
            # If file is corrupted or doesn't exist, return empty list
            return []
        except Exception as e:
            raise Exception(f"Error reading reservations file: {str(e)}")
    
    def _write_reservations(self, reservations: List[Dict[str, Any]]) -> None:
        """Write reservations to JSON file."""
        try:
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(reservations, f, indent=2, ensure_ascii=False, default=str)
        except Exception as e:
            raise Exception(f"Error writing reservations file: {str(e)}")
    
    def _reservation_to_dict(self, reservation: Reservation) -> Dict[str, Any]:
        """Convert Reservation object to dictionary."""
        return reservation.dict()
    
    def _dict_to_reservation(self, data: Dict[str, Any]) -> Reservation:
        """Convert dictionary to Reservation object."""
        # Handle date conversion if needed
        if isinstance(data.get('check_in_date'), str):
            data['check_in_date'] = date.fromisoformat(data['check_in_date'])
        if isinstance(data.get('check_out_date'), str):
            data['check_out_date'] = date.fromisoformat(data['check_out_date'])
        
        return Reservation(**data)
    
    def create_reservation(self, reservation: Reservation) -> Reservation:
        """Create a new reservation."""
        reservations = self._read_reservations()
        
        # Check if reservation ID already exists
        if any(r.get('id') == reservation.id for r in reservations):
            raise ValueError(f"Reservation with ID {reservation.id} already exists")
        
        # Add new reservation
        reservations.append(self._reservation_to_dict(reservation))
        self._write_reservations(reservations)
        
        return reservation
    
    def get_reservation(self, reservation_id: str) -> Optional[Reservation]:
        """Get reservation by ID."""
        reservations = self._read_reservations()
        
        for r in reservations:
            if r.get('id') == reservation_id:
                return self._dict_to_reservation(r)
        
        return None
    
    def update_reservation(self, reservation_id: str, updated_reservation: Reservation) -> Optional[Reservation]:
        """Update existing reservation."""
        reservations = self._read_reservations()
        
        for i, r in enumerate(reservations):
            if r.get('id') == reservation_id:
                # Ensure ID remains the same
                updated_reservation.id = reservation_id
                reservations[i] = self._reservation_to_dict(updated_reservation)
                self._write_reservations(reservations)
                return updated_reservation
        
        return None
    
    def delete_reservation(self, reservation_id: str) -> bool:
        """Delete reservation by ID."""
        reservations = self._read_reservations()
        
        for i, r in enumerate(reservations):
            if r.get('id') == reservation_id:
                reservations.pop(i)
                self._write_reservations(reservations)
                return True
        
        return False
    
    def list_reservations(self) -> List[Reservation]:
        """List all reservations."""
        reservations = self._read_reservations()
        return [self._dict_to_reservation(r) for r in reservations]
    
    def reservation_exists(self, reservation_id: str) -> bool:
        """Check if reservation exists."""
        reservations = self._read_reservations()
        return any(r.get('id') == reservation_id for r in reservations) 
    
    def _read_services(self) -> List[Dict[str, Any]]:
        """Read services from JSON file."""
        try:
            with open(self.services_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
        except (json.JSONDecodeError, FileNotFoundError):
            return []
        except Exception as e:
            raise Exception(f"Error reading services file: {str(e)}")
    
    def _write_services(self, services: List[Dict[str, Any]]) -> None:
        """Write services to JSON file."""
        try:
            with open(self.services_path, 'w', encoding='utf-8') as f:
                json.dump(services, f, indent=2, ensure_ascii=False, default=str)
        except Exception as e:
            raise Exception(f"Error writing services file: {str(e)}")
    
    def list_services(self) -> List[Dict[str, Any]]:
        """Return list of service dicts."""
        return self._read_services()
    
    def get_service(self, service_id: str) -> Optional[Dict[str, Any]]:
        """Get a single service by id."""
        services = self._read_services()
        for s in services:
            if s.get('id') == service_id:
                return s
        return None
    
    def create_service(self, service: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new service. Service is a dict with fields id,name,description,price,category,reservation_id."""
        services = self._read_services()
        
        if any(s.get('id') == service.get('id') for s in services):
            raise ValueError(f"Service with ID {service.get('id')} already exists")
        
        # Basic validation: required fields
        required = ['id', 'name', 'price']
        for field in required:
            if service.get(field) is None:
                raise ValueError(f"Service missing required field: {field}")
        
        services.append(service)
        self._write_services(services)
        return service
    
    def update_service(self, service_id: str, updated: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update an existing service by id."""
        services = self._read_services()
        for i, s in enumerate(services):
            if s.get('id') == service_id:
                # merge updates
                services[i] = {**s, **updated, "id": service_id}
                self._write_services(services)
                return services[i]
        return None
    
    def delete_service(self, service_id: str) -> bool:
        """Delete a service by id."""
        services = self._read_services()
        for i, s in enumerate(services):
            if s.get('id') == service_id:
                services.pop(i)
                self._write_services(services)
                return True
        return False
    
    def get_services_by_reservation(self, reservation_id: str) -> List[Dict[str, Any]]:
        """Return services attached to a reservation."""
        services = self._read_services()
        return [s for s in services if s.get('reservation_id') == reservation_id]