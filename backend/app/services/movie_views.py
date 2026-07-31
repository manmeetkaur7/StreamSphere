from collections.abc import Iterable
from typing import Any

from sqlalchemy import Select, func, select
from sqlalchemy.orm import selectinload

from app.models.movie import Movie
from app.models.rating import Rating
from app.models.review import Review
from app.schemas.content import GenreResponse, MovieResponse


def apply_movie_detail_load(statement: Select[Any]) -> Select[Any]:
    return statement.options(selectinload(Movie.genres))


def movie_stats_subqueries():
    ratings_subquery = (
        select(
            Rating.movie_id.label("movie_id"),
            func.avg(Rating.rating).label("average_rating"),
            func.count(Rating.id).label("total_ratings"),
        )
        .group_by(Rating.movie_id)
        .subquery()
    )
    reviews_subquery = (
        select(
            Review.movie_id.label("movie_id"),
            func.count(Review.id).label("review_count"),
        )
        .group_by(Review.movie_id)
        .subquery()
    )
    return ratings_subquery, reviews_subquery


def build_movie_select() -> Select[Any]:
    ratings_subquery, reviews_subquery = movie_stats_subqueries()
    statement = (
        select(
            Movie,
            func.coalesce(ratings_subquery.c.average_rating, 0.0).label("average_rating"),
            func.coalesce(ratings_subquery.c.total_ratings, 0).label("total_ratings"),
            func.coalesce(reviews_subquery.c.review_count, 0).label("review_count"),
        )
        .outerjoin(ratings_subquery, ratings_subquery.c.movie_id == Movie.id)
        .outerjoin(reviews_subquery, reviews_subquery.c.movie_id == Movie.id)
    )
    return apply_movie_detail_load(statement)


def movie_response_from_row(row: Any) -> MovieResponse:
    movie = row[0]
    average_rating = round(float(row.average_rating or 0.0), 2)
    return MovieResponse(
        id=movie.id,
        title=movie.title,
        description=movie.description,
        release_year=movie.release_year,
        duration_minutes=movie.duration_minutes,
        poster_url=movie.poster_url,
        trailer_url=movie.trailer_url,
        maturity_rating=movie.maturity_rating,
        language=movie.language,
        genres=[GenreResponse.model_validate(genre) for genre in movie.genres],
        average_rating=average_rating,
        total_ratings=int(row.total_ratings or 0),
        review_count=int(row.review_count or 0),
        created_at=movie.created_at,
        updated_at=movie.updated_at,
    )


def movie_response_list_from_rows(rows: Iterable[Any]) -> list[MovieResponse]:
    return [movie_response_from_row(row) for row in rows]
