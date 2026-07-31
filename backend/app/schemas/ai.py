from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.content import GenreResponse, MovieResponse


class RecommendationResponse(BaseModel):
    recommended_movies: list[MovieResponse]
    recommended_genres: list[GenreResponse]
    reason_for_recommendation: str


class AISearchRequest(BaseModel):
    query: str = Field(min_length=3, max_length=500)


class AISearchResponse(BaseModel):
    matching_movies: list[MovieResponse]
    reasoning: str
    confidence: float


class MovieSummaryResponse(BaseModel):
    movie_id: int
    short_summary: str
    long_summary: str
    main_themes: list[str]
    viewer_type: str
    provider_name: str
    generated_at: datetime
    updated_at: datetime


class ContinueWatchingItemResponse(BaseModel):
    id: int
    progress_percentage: int
    last_watched: datetime
    completed: bool
    movie: MovieResponse


class ProgressUpsertRequest(BaseModel):
    progress_percentage: int = Field(ge=0, le=100)


class ProgressResponse(BaseModel):
    id: int
    movie_id: int
    progress_percentage: int
    last_watched: datetime
    completed: bool


class HomeResponse(BaseModel):
    continue_watching: list[ContinueWatchingItemResponse]
    recommended: list[MovieResponse]
    trending: list[MovieResponse]
    favorites: list[MovieResponse]
    recently_added: list[MovieResponse]
    top_rated: list[MovieResponse]
    popular_genres: list[GenreResponse]


class AdminActionResponse(BaseModel):
    detail: str
