# app/routers/validation.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas import ValidateSentenceRequest, ValidateSentenceResponse
from app.models import PracticeSubmission, Word
from app.database import get_db
from app.utils import mock_ai_validation
from sqlalchemy import exc # สำหรับจัดการ Error

router = APIRouter()

@router.post(
    "/validate-sentence",
    response_model=ValidateSentenceResponse,
    status_code=status.HTTP_201_CREATED
)
def validate_sentence(
    request_data: ValidateSentenceRequest,
    db: Session = Depends(get_db)
):
    """
    รับประโยคและ Word ID เพื่อตรวจสอบและบันทึกผล
    """
    word_id = request_data.word_id
    submitted_sentence = request_data.sentence
    
    # 1. การดึงข้อมูลคำศัพท์
    # ดึงข้อมูลคำศัพท์ (word และ difficulty_level) จากฐานข้อมูล
    word_entry = db.query(Word).filter(Word.id == word_id).first()

    if not word_entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Word with id {word_id} not found"
        )

    # 2. Logic การตรวจสอบ (Mock AI Validation)
    validation_result = mock_ai_validation(
        sentence=submitted_sentence,
        target_word=word_entry.word,
        difficulty=word_entry.difficulty_level
    )
    
    # ดึงข้อมูลจากผลลัพธ์
    score = validation_result["score"]
    level = validation_result["level"]
    suggestion = validation_result["suggestion"]
    corrected_sentence = validation_result["corrected_sentence"]
    
    # 3. การบันทึกข้อมูล (Database/ORM)
    try:
        new_submission = PracticeSubmission(
            user_id=1,  # ตามโจทย์กำหนดให้สมมติ user_id เป็น 1
            word_id=word_id,
            submitted_sentence=submitted_sentence,
            score=score,
            feedback=suggestion,
            corrected_sentence=corrected_sentence
            # timestamp จะถูกกำหนดโดย default=datetime.utcnow ใน Model
        )
        
        db.add(new_submission)
        db.commit()
        db.refresh(new_submission) # เพื่อให้ได้ ID และ Timestamp ที่ถูกสร้างขึ้น
        
    except exc.SQLAlchemyError as e:
        db.rollback()
        # Log ข้อผิดพลาดจริงหากจำเป็น
        print(f"Database error: {e}") 
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not save practice submission to database."
        )

    # 4. Response
    # ใช้ ValidateSentenceResponse เพื่อสร้าง JSON Response
    return ValidateSentenceResponse(
        score=score,
        level=level,
        suggestion=suggestion,
        corrected_sentence=corrected_sentence
    )