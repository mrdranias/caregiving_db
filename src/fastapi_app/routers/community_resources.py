from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from sqlalchemy import text

router = APIRouter()

@router.get("/")  
async def get_community_resources(db: Session = Depends(get_db)):
    """Get all community resources for social risk recommendations"""
    try:
        query = text("""
            SELECT 
                cr.resource_id,
                cr.name,
                cr.description,
                cr.address,
                cr.city,
                cr.state,
                cr.zip_code,
                cr.phone,
                cr.website,
                sms.label as subclass_label,
                sm.label as class_label
            FROM community_resources cr
            LEFT JOIN sdoh_mitigation_subclasses sms ON cr.resource_subclass_id = sms.subclass_id
            LEFT JOIN sdoh_mitigations sm ON sms.parent_class_id = sm.class_id
            ORDER BY cr.name
        """)
        
        result = db.execute(query)
        resources = []
        
        for row in result:
            resources.append({
                "resource_id": str(row.resource_id),
                "name": row.name,
                "description": row.description,
                "address": row.address,
                "city": row.city,
                "state": row.state,
                "zip_code": row.zip_code,
                "phone": row.phone,
                "website": row.website,
                "subclass_label": row.subclass_label,
                "class_label": row.class_label
            })
        
        return {"resources": resources}
        
    except Exception as e:
        print(f"Error fetching community resources: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching community resources: {str(e)}")

@router.get("/{resource_id}")
async def get_community_resource(resource_id: str, db: Session = Depends(get_db)):
    """Get specific community resource by ID"""
    try:
        query = text("""
            SELECT 
                cr.resource_id,
                cr.name,
                cr.description,
                cr.address,
                cr.city,
                cr.state,
                cr.zip_code,
                cr.phone,
                cr.website,
                sms.label as subclass_label,
                sm.label as class_label
            FROM community_resources cr
            LEFT JOIN sdoh_mitigation_subclasses sms ON cr.resource_subclass_id = sms.subclass_id
            LEFT JOIN sdoh_mitigations sm ON sms.parent_class_id = sm.class_id
            WHERE cr.resource_id = :resource_id
        """)
        
        result = db.execute(query, {"resource_id": resource_id})
        row = result.fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail="Community resource not found")
        
        return {
            "resource_id": str(row.resource_id),
            "name": row.name,
            "description": row.description,
            "address": row.address,
            "city": row.city,
            "state": row.state,
            "zip_code": row.zip_code,
            "phone": row.phone,
            "website": row.website,
            "subclass_label": row.subclass_label,
            "class_label": row.class_label
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error fetching community resource {resource_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching community resource: {str(e)}")
