from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from database import get_db
from typing import List, Dict, Any

router = APIRouter(prefix="/contractors", tags=["contractors"])

@router.get("/")
def get_contractors(db: Session = Depends(get_db)):
    """Get all available contractors"""
    try:
        contractors = db.execute(text("""
            SELECT contractor_id, name, contact_info, qualifications 
            FROM contractors 
            ORDER BY name
        """)).fetchall()
        
        contractor_list = []
        for row in contractors:
            contractor_list.append({
                "contractor_id": str(row[0]),
                "name": row[1],
                "contact_info": row[2],
                "qualifications": row[3]
            })
        
        return {"contractors": contractor_list}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching contractors: {str(e)}")
