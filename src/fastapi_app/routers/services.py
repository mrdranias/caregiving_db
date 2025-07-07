from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from database import get_db
from typing import List, Dict, Any

router = APIRouter(prefix="/services", tags=["services"])

@router.get("/")
def get_services(db: Session = Depends(get_db)):
    """Get all available services"""
    try:
        services = db.execute(text("""
            SELECT service_id, service_name, service_category, default_frequency, description 
            FROM services 
            ORDER BY service_category, service_name
        """)).fetchall()
        
        service_list = []
        for row in services:
            service_list.append({
                "service_id": str(row[0]),
                "service_name": row[1],
                "service_category": row[2],
                "default_frequency": row[3],
                "description": row[4]
            })
        
        return {"services": service_list}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching services: {str(e)}")

@router.get("/costs")
def get_service_costs(db: Session = Depends(get_db)):
    """Get all service costs with contractor and service details"""
    try:
        costs = db.execute(text("""
            SELECT 
                c.cost_id,
                c.amount,
                c.billing_cycle,
                c.payer,
                co.contractor_id,
                co.name as contractor_name,
                s.service_id,
                s.service_name,
                s.service_category
            FROM costs c
            JOIN contractors co ON c.contractor_id = co.contractor_id
            JOIN services s ON c.service_id = s.service_id
            ORDER BY s.service_category, s.service_name, co.name
        """)).fetchall()
        
        cost_list = []
        for row in costs:
            cost_list.append({
                "cost_id": str(row[0]),
                "amount": float(row[1]) if row[1] else None,
                "billing_cycle": row[2],
                "payer": row[3],
                "contractor_id": str(row[4]),
                "contractor_name": row[5],
                "service_id": str(row[6]),
                "service_name": row[7],
                "service_category": row[8]
            })
        
        return {"costs": cost_list}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching costs: {str(e)}")
