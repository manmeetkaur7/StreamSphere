from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.content import MovieResponse


class NotificationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: UUID
    type: str
    title: str
    message: str
    is_read: bool
    created_at: datetime


class NotificationUnreadCountResponse(BaseModel):
    unread_count: int


class NotificationEventResponse(BaseModel):
    event: str
    notification: NotificationResponse
    unread_count: int


class AdminUserResponse(BaseModel):
    id: UUID
    username: str
    email: str
    is_admin: bool
    is_active: bool
    created_at: datetime


class AdminUserStatusUpdateRequest(BaseModel):
    is_active: bool


class AdminReviewResponse(BaseModel):
    id: int
    movie_id: int
    movie_title: str
    user_id: UUID
    username: str
    title: str
    body: str
    rating: int
    created_at: datetime
    updated_at: datetime


class AdminStatsResponse(BaseModel):
    total_users: int
    total_movies: int
    total_reviews: int
    total_ratings: int
    total_watchlist_entries: int
    total_favorites: int
    total_ai_searches: int
    total_recommendations_generated: int


class ActivityEventResponse(BaseModel):
    id: int
    event_type: str
    movie_id: int | None
    metadata: dict | None
    created_at: datetime


class GenreInsightResponse(BaseModel):
    name: str
    count: int


class ProfileInsightsResponse(BaseModel):
    favorite_genres: list[GenreInsightResponse]
    most_viewed_genres: list[GenreInsightResponse]
    average_rating_given: float
    movies_completed: int
    movies_in_progress: int
    total_watchlist_entries: int
    total_reviews: int
    recent_activity: list[ActivityEventResponse]


class AnalyticsMovieMetricResponse(BaseModel):
    movie: MovieResponse
    count: float


class AnalyticsGenreMetricResponse(BaseModel):
    name: str
    count: int


class DailyActiveUserResponse(BaseModel):
    day: str
    active_users: int


class PlatformAnalyticsResponse(BaseModel):
    most_viewed_movies: list[AnalyticsMovieMetricResponse]
    most_favorited_movies: list[AnalyticsMovieMetricResponse]
    most_watchlisted_movies: list[AnalyticsMovieMetricResponse]
    top_rated_movies: list[AnalyticsMovieMetricResponse]
    most_reviewed_movies: list[AnalyticsMovieMetricResponse]
    popular_genres: list[AnalyticsGenreMetricResponse]
    ai_search_volume: int
    daily_active_users: list[DailyActiveUserResponse]
