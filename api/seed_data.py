from app.database import SessionLocal, engine, Base
from app.models import Word
from sqlalchemy.exc import IntegrityError, OperationalError

def create_tables():
    print("Attempting to create database tables...")
    try:
        Base.metadata.create_all(bind=engine)
        print("Database tables ensured/created successfully!")
    except OperationalError as e:
        print(f"Error: {e}")
        raise e

def seed_data():
    db = SessionLocal()
    words_to_add = [
    { "id" : 1,"word": "Ephemeral", "definition": "Lasting for a very short time.", "difficulty_level": "Advanced" },
    { "id" : 2,"word": "Ubiquitous", "definition": "Present, appearing, or found everywhere.", "difficulty_level": "Intermediate" },
    { "id" : 3,"word": "Mellifluous", "definition": "(Of a voice or words) sweet or musical; pleasant to hear.", "difficulty_level": "Advanced" },
    { "id" : 4,"word": "Serendipity", "definition": "The occurrence and development of events by chance in a happy or beneficial way.", "difficulty_level": "Intermediate" },
    { "id" : 5,"word": "Happy", "definition": "Feeling or showing pleasure or contentment.", "difficulty_level": "Beginner" },
    { "id" : 6,"word": "Run", "definition": "Move at a speed faster than a walk, never having both or all the feet on the ground at the same time.", "difficulty_level": "Beginner" }
]

    try:
        print("Starting data seeding...")
        for data in words_to_add:
            existing = db.query(Word).filter(Word.id == data['id']).first()
            if not existing:
                new_word = Word(
                    id=data['id'], word=data['word'], 
                    definition=data['definition'], difficulty_level=data['difficulty_level']
                )
                db.add(new_word)
                print(f" - Inserted: {data['word']}")
            else:
                print(f" - Exists: {data['word']}")
        db.commit()
        print("Done.")
    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    create_tables()
    seed_data()