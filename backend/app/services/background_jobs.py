from fastapi import BackgroundTasks
from app.db.session import SessionLocal
from app.models.movie import Movie
from app.models.user import User
from app.services.ai_provider import get_ai_provider
from app.services.notification_service import create_notification
from app.services.recommendation_service import compute_recommendations
from app.services.summary_service import get_or_generate_summary


async def _create_notification_job(
    user_id: object,
    notification_type: str,
    title: str,
    message: str,
) -> None:
    with SessionLocal() as db:
        user = db.get(User, user_id)
        if user is None:
            return
        await create_notification(
            db,
            user_id=user.id,
            notification_type=notification_type,
            title=title,
            message=message,
        )


def _refresh_recommendation_cache_job(user_id: object) -> None:
    with SessionLocal() as db:
        user = db.get(User, user_id)
        if user is None:
            return
        payload = compute_recommendations(db, user, persist=True)
        if payload.recommended_movies:
            import asyncio

            asyncio.run(
                create_notification(
                    db,
                    user_id=user.id,
                    notification_type="recommendation_ready",
                    title="Recommendations ready",
                    message=f"{len(payload.recommended_movies)} fresh picks are ready for you.",
                )
            )


def _generate_summary_job(movie_id: int) -> None:
    with SessionLocal() as db:
        movie = db.get(Movie, movie_id)
        if movie is None:
            return
        provider = get_ai_provider()
        get_or_generate_summary(db, provider, movie_id, force=True)


class BackgroundJobDispatcher:
    def queue_notification(
        self,
        background_tasks: BackgroundTasks,
        *,
        user_id: object,
        notification_type: str,
        title: str,
        message: str,
    ) -> None:
        background_tasks.add_task(
            _create_notification_job,
            user_id,
            notification_type,
            title,
            message,
        )

    def queue_recommendation_refresh(self, background_tasks: BackgroundTasks, *, user_id: object) -> None:
        background_tasks.add_task(_refresh_recommendation_cache_job, user_id)

    def queue_summary_generation(self, background_tasks: BackgroundTasks, *, movie_id: int) -> None:
        background_tasks.add_task(_generate_summary_job, movie_id)


background_job_dispatcher = BackgroundJobDispatcher()
