from app.models.favorite import Favorite
from app.models.genre import Genre
from app.models.movie import Movie
from app.models.movie_genre import MovieGenre
from app.models.movie_summary import MovieSummary
from app.models.rating import Rating
from app.models.recommendation_cache import RecommendationCache
from app.models.review import Review
from app.models.user import User
from app.models.watch_progress import WatchProgress
from app.models.watchlist import Watchlist

__all__ = [
    "Favorite",
    "Genre",
    "Movie",
    "MovieGenre",
    "MovieSummary",
    "Rating",
    "RecommendationCache",
    "Review",
    "User",
    "WatchProgress",
    "Watchlist",
]
