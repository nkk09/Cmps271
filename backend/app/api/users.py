from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.user import User
from sqlalchemy import Column, Integer, String
from app.db.base_class import Base

router = APIRouter()

# ---- REVIEW MODEL (temporary inside same file) ----
class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(String, nullable=False)


# ---------------- REVIEWS CRUD ----------------

@router.get("/reviews")
def get_reviews(db: Session = Depends(get_db)):
    return db.query(Review).all()


@router.post("/reviews")
def create_review(review: dict, db: Session = Depends(get_db)):
    db_review = Review(content=review["content"])
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
    return db_review


@router.put("/reviews/{review_id}")
def update_review(review_id: int, review: dict, db: Session = Depends(get_db)):
    db_review = db.query(Review).filter(Review.id == review_id).first()
    db_review.content = review["content"]
    db.commit()
    db.refresh(db_review)
    return db_review


@router.delete("/reviews/{review_id}")
def delete_review(review_id: int, db: Session = Depends(get_db)):
    db_review = db.query(Review).filter(Review.id == review_id).first()
    db.delete(db_review)
    db.commit()
    return {"message": "Deleted"}