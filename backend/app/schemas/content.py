from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class GenreBase(BaseModel):
    name: str = Field(min_length=2, max_length=80)


class GenreCreate(GenreBase):
    pass


class GenreUpdate(GenreBase):
    pass


class GenreResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


class MovieBase(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str = Field(min_length=10, max_length=5000)
    release_year: int = Field(ge=1888, le=2100)
    duration_minutes: int = Field(ge=1, le=600)
    poster_url: HttpUrl
    trailer_url: HttpUrl
    maturity_rating: str = Field(min_length=1, max_length=16)
    language: str = Field(min_length=2, max_length=80)
    genre_ids: list[int] = Field(min_length=1)


class CreateMovie(MovieBase):
    pass


class UpdateMovie(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, min_length=10, max_length=5000)
    release_year: int | None = Field(default=None, ge=1888, le=2100)
    duration_minutes: int | None = Field(default=None, ge=1, le=600)
    poster_url: HttpUrl | None = None
    trailer_url: HttpUrl | None = None
    maturity_rating: str | None = Field(default=None, min_length=1, max_length=16)
    language: str | None = Field(default=None, min_length=2, max_length=80)
    genre_ids: list[int] | None = Field(default=None, min_length=1)


class MovieResponse(BaseModel):
    id: int
    title: str
    description: str
    release_year: int
    duration_minutes: int
    poster_url: HttpUrl
    trailer_url: HttpUrl
    maturity_rating: str
    language: str
    genres: list[GenreResponse]
    average_rating: float
    total_ratings: int
    review_count: int
    created_at: datetime
    updated_at: datetime


class MovieListResponse(BaseModel):
    items: list[MovieResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


SortBy = Literal["title", "release_year"]
SortOrder = Literal["asc", "desc"]
