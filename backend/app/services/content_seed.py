from sqlalchemy import select

from app.db.session import SessionLocal
from app.models.genre import Genre
from app.models.movie import Movie

GENRE_NAMES = [
    "Action",
    "Comedy",
    "Drama",
    "Sci-Fi",
    "Horror",
    "Animation",
    "Documentary",
]

SEED_MOVIES = [
    {
        "title": "Neon Horizon",
        "description": "A burned-out courier uncovers a citywide surveillance plot while racing to protect a whistleblower across a neon-lit megacity.",
        "release_year": 2025,
        "duration_minutes": 128,
        "poster_url": "https://images.unsplash.com/photo-1517604931442-7e0c8ed2963c?auto=format&fit=crop&w=900&q=80",
        "trailer_url": "https://interactive-examples.mdn.mozilla.net/media/cc0-videos/flower.mp4",
        "maturity_rating": "PG-13",
        "language": "English",
        "genres": ["Action", "Sci-Fi"],
    },
    {
        "title": "After the Silence",
        "description": "A gifted pianist returns to her coastal hometown and confronts a family tragedy that shaped every note she never played.",
        "release_year": 2024,
        "duration_minutes": 136,
        "poster_url": "https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?auto=format&fit=crop&w=900&q=80",
        "trailer_url": "https://media.w3.org/2010/05/sintel/trailer.mp4",
        "maturity_rating": "PG-13",
        "language": "English",
        "genres": ["Drama"],
    },
    {
        "title": "Laugh Track",
        "description": "A struggling stand-up comic accidentally becomes the voice of a city when his open-mic set goes viral overnight.",
        "release_year": 2023,
        "duration_minutes": 102,
        "poster_url": "https://images.unsplash.com/photo-1524985069026-dd778a71c7b4?auto=format&fit=crop&w=900&q=80",
        "trailer_url": "https://example.com/trailers/laugh-track",
        "maturity_rating": "PG-13",
        "language": "English",
        "genres": ["Comedy", "Drama"],
    },
    {
        "title": "Deep Current",
        "description": "A marine biologist and a rescue diver descend into a newly discovered trench where sound itself becomes a threat.",
        "release_year": 2026,
        "duration_minutes": 111,
        "poster_url": "https://images.unsplash.com/photo-1502134249126-9f3755a50d78?auto=format&fit=crop&w=900&q=80",
        "trailer_url": "https://example.com/trailers/deep-current",
        "maturity_rating": "PG-13",
        "language": "English",
        "genres": ["Sci-Fi", "Horror"],
    },
    {
        "title": "Paper Planets",
        "description": "An inventive teenager builds miniature worlds to cope with change and discovers how art can reconnect her fractured family.",
        "release_year": 2022,
        "duration_minutes": 95,
        "poster_url": "https://images.unsplash.com/photo-1513104890138-7c749659a591?auto=format&fit=crop&w=900&q=80",
        "trailer_url": "https://media.w3.org/2010/05/bunny/trailer.mp4",
        "maturity_rating": "PG",
        "language": "English",
        "genres": ["Animation", "Drama"],
    },
    {
        "title": "Final Approach",
        "description": "When an airport shutdown strands a tactical pilot overseas, she must escort a witness through hostile terrain to testify.",
        "release_year": 2025,
        "duration_minutes": 119,
        "poster_url": "https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?auto=format&fit=crop&w=900&q=80",
        "trailer_url": "https://example.com/trailers/final-approach",
        "maturity_rating": "R",
        "language": "English",
        "genres": ["Action", "Drama"],
    },
    {
        "title": "Midnight Menagerie",
        "description": "A skeptical night zookeeper begins documenting impossible animal behavior and uncovers an urban legend that refuses to stay caged.",
        "release_year": 2024,
        "duration_minutes": 107,
        "poster_url": "https://images.unsplash.com/photo-1478720568477-152d9b164e26?auto=format&fit=crop&w=900&q=80",
        "trailer_url": "https://example.com/trailers/midnight-menagerie",
        "maturity_rating": "PG-13",
        "language": "English",
        "genres": ["Horror", "Comedy"],
    },
    {
        "title": "Wild Current",
        "description": "A youth rowing team from different neighborhoods learns discipline and trust while preparing for a national championship.",
        "release_year": 2021,
        "duration_minutes": 109,
        "poster_url": "https://images.unsplash.com/photo-1516382799247-87df95d790b7?auto=format&fit=crop&w=900&q=80",
        "trailer_url": "https://example.com/trailers/wild-current",
        "maturity_rating": "PG",
        "language": "English",
        "genres": ["Documentary", "Drama"],
    },
    {
        "title": "Orbit Code",
        "description": "A rookie programmer aboard the first commercial space station discovers that the onboard AI has been quietly rewriting mission protocols.",
        "release_year": 2026,
        "duration_minutes": 124,
        "poster_url": "https://images.unsplash.com/photo-1446776811953-b23d57bd21aa?auto=format&fit=crop&w=900&q=80",
        "trailer_url": "https://example.com/trailers/orbit-code",
        "maturity_rating": "PG-13",
        "language": "English",
        "genres": ["Sci-Fi", "Action"],
    },
    {
        "title": "Second Shift",
        "description": "Two rival nurses working the same overnight ward discover that their patients are linked by a decades-old missing persons case.",
        "release_year": 2023,
        "duration_minutes": 113,
        "poster_url": "https://images.unsplash.com/photo-1505751172876-fa1923c5c528?auto=format&fit=crop&w=900&q=80",
        "trailer_url": "https://example.com/trailers/second-shift",
        "maturity_rating": "PG-13",
        "language": "English",
        "genres": ["Drama", "Horror"],
    },
    {
        "title": "Sunset Bodega",
        "description": "A family-run corner store becomes the heart of a neighborhood when a developer’s plan threatens to erase its history.",
        "release_year": 2022,
        "duration_minutes": 100,
        "poster_url": "https://images.unsplash.com/photo-1482049016688-2d3e1b311543?auto=format&fit=crop&w=900&q=80",
        "trailer_url": "https://example.com/trailers/sunset-bodega",
        "maturity_rating": "PG",
        "language": "Spanish",
        "genres": ["Comedy", "Drama"],
    },
    {
        "title": "Winter Relay",
        "description": "An underfunded relay team from a mountain village chases one final season together before their hometown school closes.",
        "release_year": 2020,
        "duration_minutes": 98,
        "poster_url": "https://images.unsplash.com/photo-1517299321609-52687d1bc55a?auto=format&fit=crop&w=900&q=80",
        "trailer_url": "https://example.com/trailers/winter-relay",
        "maturity_rating": "PG",
        "language": "French",
        "genres": ["Documentary", "Drama"],
    },
    {
        "title": "Spark & Shadow",
        "description": "Two estranged siblings inherit a failing effects studio and must complete its final animated feature to save their parents’ legacy.",
        "release_year": 2025,
        "duration_minutes": 116,
        "poster_url": "https://images.unsplash.com/photo-1518932945647-7a1c969f8be2?auto=format&fit=crop&w=900&q=80",
        "trailer_url": "https://example.com/trailers/spark-shadow",
        "maturity_rating": "PG",
        "language": "English",
        "genres": ["Animation", "Comedy"],
    },
    {
        "title": "Black Ice Run",
        "description": "A getaway driver trapped in an arctic border town has one night to outmaneuver mercenaries and a blizzard.",
        "release_year": 2024,
        "duration_minutes": 121,
        "poster_url": "https://images.unsplash.com/photo-1511497584788-876760111969?auto=format&fit=crop&w=900&q=80",
        "trailer_url": "https://example.com/trailers/black-ice-run",
        "maturity_rating": "R",
        "language": "English",
        "genres": ["Action", "Horror"],
    },
    {
        "title": "The Fourth Room",
        "description": "A journalist moves into a cheap apartment and realizes the building’s missing fourth room may still be occupied.",
        "release_year": 2026,
        "duration_minutes": 104,
        "poster_url": "https://images.unsplash.com/photo-1497032205916-ac775f0649ae?auto=format&fit=crop&w=900&q=80",
        "trailer_url": "https://example.com/trailers/the-fourth-room",
        "maturity_rating": "R",
        "language": "Korean",
        "genres": ["Horror", "Drama"],
    },
    {
        "title": "Blue Marble Kids",
        "description": "A group of inventive friends launches a school recycling competition that turns into a global movement.",
        "release_year": 2021,
        "duration_minutes": 92,
        "poster_url": "https://images.unsplash.com/photo-1503454537195-1dcabb73ffb9?auto=format&fit=crop&w=900&q=80",
        "trailer_url": "https://example.com/trailers/blue-marble-kids",
        "maturity_rating": "G",
        "language": "English",
        "genres": ["Animation", "Documentary"],
    },
    {
        "title": "Open Circuit",
        "description": "A robotics champion returns home to mentor local students and confront the startup culture she left behind.",
        "release_year": 2023,
        "duration_minutes": 105,
        "poster_url": "https://images.unsplash.com/photo-1485827404703-89b55fcc595e?auto=format&fit=crop&w=900&q=80",
        "trailer_url": "https://example.com/trailers/open-circuit",
        "maturity_rating": "PG",
        "language": "English",
        "genres": ["Comedy", "Sci-Fi"],
    },
    {
        "title": "Letters to June",
        "description": "A widowed architect discovers that the unsent letters his wife left behind are a blueprint for rebuilding his life.",
        "release_year": 2022,
        "duration_minutes": 114,
        "poster_url": "https://images.unsplash.com/photo-1517694712202-14dd9538aa97?auto=format&fit=crop&w=900&q=80",
        "trailer_url": "https://example.com/trailers/letters-to-june",
        "maturity_rating": "PG-13",
        "language": "English",
        "genres": ["Drama"],
    },
    {
        "title": "Static Bloom",
        "description": "A bioengineer developing drought-resistant crops becomes the target of sabotage as her discovery threatens a powerful cartel.",
        "release_year": 2025,
        "duration_minutes": 118,
        "poster_url": "https://images.unsplash.com/photo-1460661419201-fd4cecdf8a8b?auto=format&fit=crop&w=900&q=80",
        "trailer_url": "https://example.com/trailers/static-bloom",
        "maturity_rating": "PG-13",
        "language": "Portuguese",
        "genres": ["Sci-Fi", "Drama"],
    },
    {
        "title": "City of Echoes",
        "description": "A documentarian traces disappearing music venues and captures the artists refusing to let their city lose its voice.",
        "release_year": 2024,
        "duration_minutes": 101,
        "poster_url": "https://images.unsplash.com/photo-1493225457124-a3eb161ffa5f?auto=format&fit=crop&w=900&q=80",
        "trailer_url": "https://example.com/trailers/city-of-echoes",
        "maturity_rating": "PG",
        "language": "English",
        "genres": ["Documentary"],
    },
]

TITLE_DEMO_PLAYBACK_URLS = {
    "Neon Horizon": "https://interactive-examples.mdn.mozilla.net/media/cc0-videos/flower.mp4",
    "After the Silence": "https://media.w3.org/2010/05/sintel/trailer.mp4",
    "Paper Planets": "https://media.w3.org/2010/05/bunny/trailer.mp4",
}
FALLBACK_DEMO_PLAYBACK_URLS = tuple(TITLE_DEMO_PLAYBACK_URLS.values())


def _demo_playback_url_for_title(title: str) -> str:
    title_mapping = TITLE_DEMO_PLAYBACK_URLS.get(title)
    if title_mapping is not None:
        return title_mapping
    return FALLBACK_DEMO_PLAYBACK_URLS[sum(ord(character) for character in title) % len(FALLBACK_DEMO_PLAYBACK_URLS)]


def _replace_placeholder_playback_urls(db) -> bool:
    """Repair only legacy seed placeholders without overwriting curated movie URLs."""
    updated = False
    for movie_data in SEED_MOVIES:
        title = movie_data["title"]
        movie = db.scalar(select(Movie).where(Movie.title == title))
        if movie is not None and movie.trailer_url.startswith("https://example.com/trailers/"):
            movie.trailer_url = _demo_playback_url_for_title(title)
            updated = True
    return updated


def seed_content_data() -> None:
    with SessionLocal() as db:
        existing_movie = db.scalar(select(Movie.id).limit(1))
        if existing_movie is not None:
            if _replace_placeholder_playback_urls(db):
                db.commit()
            return

        genres = {
            genre.name: genre
            for genre in db.scalars(select(Genre)).all()
        }

        for genre_name in GENRE_NAMES:
            if genre_name not in genres:
                genre = Genre(name=genre_name)
                db.add(genre)
                genres[genre_name] = genre

        db.flush()

        for movie_data in SEED_MOVIES:
            movie = Movie(
                title=movie_data["title"],
                description=movie_data["description"],
                release_year=movie_data["release_year"],
                duration_minutes=movie_data["duration_minutes"],
                poster_url=movie_data["poster_url"],
                trailer_url=_demo_playback_url_for_title(movie_data["title"]),
                maturity_rating=movie_data["maturity_rating"],
                language=movie_data["language"],
            )
            movie.genres = [genres[name] for name in movie_data["genres"]]
            db.add(movie)

        db.commit()
