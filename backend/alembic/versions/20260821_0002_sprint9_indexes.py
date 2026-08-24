"""sprint 9 performance indexes

Revision ID: 20260821_0002
Revises: 20260821_0001
Create Date: 2026-08-21 10:30:00
"""

from collections.abc import Iterable

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision = "20260821_0002"
down_revision = "20260821_0001"
branch_labels = None
depends_on = None


def _existing_indexes(table_name: str) -> set[str]:
    return {index["name"] for index in inspect(op.get_bind()).get_indexes(table_name)}


def _create_index_if_missing(name: str, table_name: str, columns: Iterable[str]) -> None:
    if name not in _existing_indexes(table_name):
        op.create_index(name, table_name, list(columns))


def _drop_index_if_present(name: str, table_name: str) -> None:
    if name in _existing_indexes(table_name):
        op.drop_index(name, table_name=table_name)


def upgrade() -> None:
    _create_index_if_missing("ix_movies_created_at_id", "movies", ("created_at", "id"))
    _create_index_if_missing("ix_movies_language_release_year", "movies", ("language", "release_year"))
    _create_index_if_missing("ix_favorites_movie_created_at", "favorites", ("movie_id", "created_at"))
    _create_index_if_missing("ix_ratings_movie_created_at", "ratings", ("movie_id", "created_at"))
    _create_index_if_missing("ix_ratings_user_created_at", "ratings", ("user_id", "created_at"))
    _create_index_if_missing("ix_watchlists_movie_created_at", "watchlists", ("movie_id", "created_at"))
    _create_index_if_missing(
        "ix_watch_progress_user_completed_last_watched",
        "watch_progress",
        ("user_id", "completed", "last_watched"),
    )
    _create_index_if_missing(
        "ix_notifications_user_read_created_at",
        "notifications",
        ("user_id", "is_read", "created_at"),
    )
    _create_index_if_missing(
        "ix_activity_events_user_type_created_at",
        "activity_events",
        ("user_id", "event_type", "created_at"),
    )
    _create_index_if_missing(
        "ix_movie_genres_genre_id_movie_id",
        "movie_genres",
        ("genre_id", "movie_id"),
    )


def downgrade() -> None:
    _drop_index_if_present("ix_movie_genres_genre_id_movie_id", "movie_genres")
    _drop_index_if_present("ix_activity_events_user_type_created_at", "activity_events")
    _drop_index_if_present("ix_notifications_user_read_created_at", "notifications")
    _drop_index_if_present("ix_watch_progress_user_completed_last_watched", "watch_progress")
    _drop_index_if_present("ix_watchlists_movie_created_at", "watchlists")
    _drop_index_if_present("ix_ratings_user_created_at", "ratings")
    _drop_index_if_present("ix_ratings_movie_created_at", "ratings")
    _drop_index_if_present("ix_favorites_movie_created_at", "favorites")
    _drop_index_if_present("ix_movies_language_release_year", "movies")
    _drop_index_if_present("ix_movies_created_at_id", "movies")
