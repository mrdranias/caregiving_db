from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from database import get_db

router = APIRouter(prefix="/codes", tags=["codes"])

@router.get("/dx")
def get_dx_codes(db: Session = Depends(get_db)):
    rows = db.execute(text('''
        SELECT c.code, c.description, COUNT(u.code) as freq
        FROM dx_codes c
        LEFT JOIN (
            SELECT unnest(dx_codes) as code FROM patient_history
        ) u ON c.code = u.code
        GROUP BY c.code, c.description
        ORDER BY freq DESC
        LIMIT 20
    ''')).fetchall()
    return [{"code": r[0], "description": r[1]} for r in rows]

@router.get("/tx")
def get_tx_codes(db: Session = Depends(get_db)):
    rows = db.execute(text('''
        SELECT c.code, c.description, COUNT(u.code) as freq
        FROM tx_codes c
        LEFT JOIN (
            SELECT unnest(tx_codes) as code FROM patient_history
        ) u ON c.code = u.code
        GROUP BY c.code, c.description
        ORDER BY freq DESC
        LIMIT 20
    ''')).fetchall()
    return [{"code": r[0], "description": r[1]} for r in rows]

@router.get("/rx")
def get_rx_codes(db: Session = Depends(get_db)):
    rows = db.execute(text('''
        SELECT c.code, c.description, COUNT(u.code) as freq
        FROM rx_codes c
        LEFT JOIN (
            SELECT unnest(rx_codes) as code FROM patient_history
        ) u ON c.code = u.code
        GROUP BY c.code, c.description
        ORDER BY freq DESC
        LIMIT 20
    ''')).fetchall()
    return [{"code": r[0], "description": r[1]} for r in rows]

@router.get("/sx")
def get_sx_codes(db: Session = Depends(get_db)):
    rows = db.execute(text('''
        SELECT c.code, c.description, COUNT(u.code) as freq
        FROM sx_codes c
        LEFT JOIN (
            SELECT unnest(sx_codes) as code FROM patient_history
        ) u ON c.code = u.code
        GROUP BY c.code, c.description
        ORDER BY freq DESC
        LIMIT 20
    '''))
    rows = rows.fetchall()
    return [{"code": r[0], "description": r[1]} for r in rows]
