from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.content import MovieResponse


class RatingRequest(BaseModel):
    rating: int = Field(ge=1, le=5)


class RatingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: UUID
    movie_id: int
    rating: int
    created_at: datetime
    updated_at: datetime


class ReviewCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    body: str = Field(min_length=10, max_length=5000)
    rating: int = Field(ge=1, le=5)


class ReviewUpdateRequest(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    body: str | None = Field(default=None, min_length=10, max_length=5000)
    rating: int | None = Field(default=None, ge=1, le=5)


class ReviewResponse(BaseModel):
    id: int
    movie_id: int
    user_id: UUID
    username: str
    title: str
    body: str
    rating: int
    created_at: datetime
    updated_at: datetime


class WatchlistItemResponse(BaseModel):
    id: int
    created_at: datetime
    movie: MovieResponse


class FavoriteItemResponse(BaseModel):
    id: int
    created_at: datetime
    movie: MovieResponse


class ProfileReviewResponse(ReviewResponse):
    movie_title: str


class ProfileResponse(BaseModel):
    username: str
    email: str
    is_admin: bool
    account_creation_date: datetime
    favorite_count: int
    watchlist_count: int
    review_count: int
    average_rating_given: float
    recent_reviews: list[ProfileReviewResponse]
    favorite_movies: list[MovieResponse]
    watchlist_movies: list[MovieResponse]
