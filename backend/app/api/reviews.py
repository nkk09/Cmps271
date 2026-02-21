"""
Review endpoints - list reviews, create reviews, like/dislike reviews.
"""

from datetime import datetime
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
from app.core.database import get_db
from app.core.session import require_user
from app.core.logger import get_logger
from app.models.user import User
from app.models.review import Review
from app.models.review_interaction import ReviewInteraction
from app.models.course import Course
from app.models.course_section import CourseSection
from app.models.professor import Professor
from app.schemas.review import (
    ReviewCreate,
    ReviewUpdate,
    ReviewResponse,
    ReviewDetailResponse,
    ReviewListResponse,
)

router = APIRouter()
logger = get_logger(__name__)


def _build_review_response(review: Review) -> ReviewResponse:
    """Convert review to response format with anonymity enforced."""
    return ReviewResponse(
        id=review.id,
        title=review.title,
        content=review.content,
        rating=review.rating,
        attributes=review.attributes,
        reviewer_username=review.user.username,  # Anonymous only
        course_number=review.course.course_number,
        professor_name=review.professor.full_name,
        likes_count=review.likes_count,
        dislikes_count=review.dislikes_count,
        net_rating=review.net_rating,
        created_at=review.created_at,
    )


@router.get("/reviews", response_model=ReviewListResponse)
def list_reviews(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_user),
    course_id: int = Query(None),
    professor_id: int = Query(None),
    section_id: int = Query(None),
    semester: str = Query(None),
    rating_min: float = Query(None),
    rating_max: float = Query(None),
    sort_by: str = Query("created_at"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    """
    List reviews with filtering and pagination.
    Only approved reviews are returned (anonymity).
    
    Query parameters:
    - course_id: Filter by course
    - professor_id: Filter by professor
    - section_id: Filter by section
    - semester: Filter by semester
    - rating_min: Minimum rating (1-5)
    - rating_max: Maximum rating (1-5)
    - sort_by: Sort by 'created_at', 'rating', or 'net_rating'
    - page: Page number (default 1)
    - page_size: Items per page (default 20, max 100)
    """
    # Only query approved reviews for regular users
    query = db.query(Review).filter(
        and_(
            Review.status == "approved",
            Review.deleted_at == None,
        )
    )
    
    if course_id:
        query = query.filter(Review.course_id == course_id)
    
    if professor_id:
        query = query.filter(Review.professor_id == professor_id)
    
    if section_id:
        query = query.filter(Review.section_id == section_id)
    
    if semester:
        query = query.filter(Review.section.has(CourseSection.semester == semester))
    
    if rating_min is not None:
        query = query.filter(Review.rating >= rating_min)
    
    if rating_max is not None:
        query = query.filter(Review.rating <= rating_max)
    
    # Sort
    if sort_by == "rating":
        query = query.order_by(desc(Review.rating))
    elif sort_by == "net_rating":
        # Sort by likes - dislikes
        from sqlalchemy import desc, literal_column
        query = query.order_by(desc(Review.likes_count - Review.dislikes_count))
    else:  # created_at (default)
        query = query.order_by(desc(Review.created_at))
    
    # Pagination
    total = query.count()
    reviews = query.offset((page - 1) * page_size).limit(page_size).all()
    
    return ReviewListResponse(
        items=[_build_review_response(review) for review in reviews],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/reviews/{review_id}", response_model=ReviewDetailResponse)
def get_review(
    review_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_user),
):
    """Get a specific review (approved only, or own pending review)."""
    review = db.query(Review).filter(Review.id == review_id).first()
    
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )
    
    # Only show approved reviews or own pending reviews
    if review.status != "approved" and review.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this review"
        )
    
    if review.deleted_at is not None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review has been deleted"
        )
    
    return ReviewDetailResponse(
        id=review.id,
        title=review.title,
        content=review.content,
        rating=review.rating,
        attributes=review.attributes,
        reviewer_username=review.user.username,
        course_number=review.course.course_number,
        professor_name=review.professor.full_name,
        likes_count=review.likes_count,
        dislikes_count=review.dislikes_count,
        net_rating=review.net_rating,
        created_at=review.created_at,
        status=review.status,
        semester=review.section.semester if review.section else None,
        year=review.section.year if review.section else None,
        updated_at=review.updated_at,
    )


@router.post("/reviews", response_model=ReviewDetailResponse, status_code=status.HTTP_201_CREATED)
def create_review(
    review_data: ReviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_user),
):
    """
    Create a new review.
    Reviews are set to 'pending' status and require admin approval before visibility.
    """
    # Validate course exists
    course = db.query(Course).filter(Course.id == review_data.course_id).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Course not found"
        )
    
    # Validate professor exists
    professor = db.query(Professor).filter(Professor.id == review_data.professor_id).first()
    if not professor:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Professor not found"
        )
    
    # Validate section exists if provided
    if review_data.section_id:
        section = db.query(CourseSection).filter(
            CourseSection.id == review_data.section_id
        ).first()
        if not section or section.course_id != review_data.course_id or section.professor_id != review_data.professor_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid section"
            )
    
    # Create review (pending approval)
    review = Review(
        user_id=current_user.id,
        course_id=review_data.course_id,
        professor_id=review_data.professor_id,
        section_id=review_data.section_id,
        title=review_data.title,
        content=review_data.content,
        rating=review_data.rating,
        attributes=review_data.attributes,
        status="pending",  # Requires moderation before visibility
    )
    
    db.add(review)
    db.commit()
    db.refresh(review)
    
    logger.info(f"Review created by user {current_user.id}: {review.id}")
    
    return ReviewDetailResponse(
        id=review.id,
        title=review.title,
        content=review.content,
        rating=review.rating,
        attributes=review.attributes,
        reviewer_username=review.user.username,
        course_number=review.course.course_number,
        professor_name=review.professor.full_name,
        likes_count=review.likes_count,
        dislikes_count=review.dislikes_count,
        net_rating=review.net_rating,
        created_at=review.created_at,
        status=review.status,
        semester=review.section.semester if review.section else None,
        year=review.section.year if review.section else None,
        updated_at=review.updated_at,
    )


@router.put("/reviews/{review_id}", response_model=ReviewDetailResponse)
def update_review(
    review_id: int,
    review_data: ReviewUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_user),
):
    """
    Update own review.
    Can only update own reviews, and only sensitive fields.
    """
    review = db.query(Review).filter(Review.id == review_id).first()
    
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )
    
    # Only owner can update
    if review.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only edit your own reviews"
        )
    
    # Can't edit deleted reviews
    if review.deleted_at is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot edit deleted reviews"
        )
    
    # Update fields
    if review_data.title is not None:
        review.title = review_data.title
    if review_data.content is not None:
        review.content = review_data.content
    if review_data.rating is not None:
        review.rating = review_data.rating
    if review_data.attributes is not None:
        review.attributes = review_data.attributes
    
    db.commit()
    db.refresh(review)
    
    logger.info(f"Review {review_id} updated by user {current_user.id}")
    
    return ReviewDetailResponse(
        id=review.id,
        title=review.title,
        content=review.content,
        rating=review.rating,
        attributes=review.attributes,
        reviewer_username=review.user.username,
        course_number=review.course.course_number,
        professor_name=review.professor.full_name,
        likes_count=review.likes_count,
        dislikes_count=review.dislikes_count,
        net_rating=review.net_rating,
        created_at=review.created_at,
        status=review.status,
        semester=review.section.semester if review.section else None,
        year=review.section.year if review.section else None,
        updated_at=review.updated_at,
    )


@router.delete("/reviews/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_review(
    review_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_user),
):
    """
    Delete own review (soft delete - preserves moderation history).
    """
    review = db.query(Review).filter(Review.id == review_id).first()
    
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )
    
    # Only owner can delete
    if review.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own reviews"
        )
    
    # Soft delete
    review.deleted_at = datetime.utcnow()
    
    db.commit()
    
    logger.info(f"Review {review_id} deleted by user {current_user.id}")
    
    return None


@router.post("/reviews/{review_id}/like", status_code=status.HTTP_201_CREATED)
def like_review(
    review_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_user),
):
    """Like a review - affects smart ranking."""
    review = db.query(Review).filter(Review.id == review_id).first()
    
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )
    
    if review.status != "approved" or review.deleted_at is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot interact with this review"
        )
    
    # Check if user already interacted
    existing = db.query(ReviewInteraction).filter(
        and_(
            ReviewInteraction.review_id == review_id,
            ReviewInteraction.user_id == current_user.id,
        )
    ).first()
    
    if existing:
        if existing.interaction_type == "like":
            # Remove like
            db.delete(existing)
            review.likes_count = max(0, review.likes_count - 1)
        else:  # was dislike
            # Change from dislike to like
            review.dislikes_count = max(0, review.dislikes_count - 1)
            existing.interaction_type = "like"
            review.likes_count += 1
    else:
        # Add new like
        interaction = ReviewInteraction(
            review_id=review_id,
            user_id=current_user.id,
            interaction_type="like",
        )
        db.add(interaction)
        review.likes_count += 1
    
    db.commit()
    
    logger.info(f"User {current_user.id} liked review {review_id}")
    
    return {"status": "success", "likes_count": review.likes_count, "dislikes_count": review.dislikes_count}


@router.post("/reviews/{review_id}/dislike", status_code=status.HTTP_201_CREATED)
def dislike_review(
    review_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_user),
):
    """Dislike a review - affects smart ranking."""
    review = db.query(Review).filter(Review.id == review_id).first()
    
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )
    
    if review.status != "approved" or review.deleted_at is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot interact with this review"
        )
    
    # Check if user already interacted
    existing = db.query(ReviewInteraction).filter(
        and_(
            ReviewInteraction.review_id == review_id,
            ReviewInteraction.user_id == current_user.id,
        )
    ).first()
    
    if existing:
        if existing.interaction_type == "dislike":
            # Remove dislike
            db.delete(existing)
            review.dislikes_count = max(0, review.dislikes_count - 1)
        else:  # was like
            # Change from like to dislike
            review.likes_count = max(0, review.likes_count - 1)
            existing.interaction_type = "dislike"
            review.dislikes_count += 1
    else:
        # Add new dislike
        interaction = ReviewInteraction(
            review_id=review_id,
            user_id=current_user.id,
            interaction_type="dislike",
        )
        db.add(interaction)
        review.dislikes_count += 1
    
    db.commit()
    
    logger.info(f"User {current_user.id} disliked review {review_id}")
    
    return {"status": "success", "likes_count": review.likes_count, "dislikes_count": review.dislikes_count}
