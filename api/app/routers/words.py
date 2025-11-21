from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Word
from app.schemas import WordResponse
import random

router = APIRouter()

@router.get("/word", response_model=WordResponse)
def get_random_word(db: Session = Depends(get_db)):
    # 1. เช็คจำนวนคำใน Database (นี่คือการใช้ DB ครั้งที่ 1)
    count = db.query(Word).count()
    
    if count == 0:
        raise HTTPException(status_code=404, detail="No words found in database")
    
    # 2. สุ่มตำแหน่ง
    random_offset = random.randint(0, count - 1)
    
    # 3. ดึงคำศัพท์จาก Database จริงๆ
    word = db.query(Word).offset(random_offset).first()
    
    return word