import os

from locust import HttpUser, between, task


class StreamSphereUser(HttpUser):
    wait_time = between(1, 3)
    host = os.getenv("STREAMSPHERE_BASE_URL", "http://127.0.0.1:8000")

    def on_start(self) -> None:
        self.token = None
        username = os.getenv("STREAMSPHERE_LOADTEST_USERNAME")
        password = os.getenv("STREAMSPHERE_LOADTEST_PASSWORD")
        if username and password:
            response = self.client.post(
                "/auth/login",
                data={"username": username, "password": password},
                name="/auth/login",
            )
            if response.ok:
                self.token = response.json().get("access_token")

    def _auth_headers(self) -> dict[str, str]:
        if not self.token:
            return {}
        return {"Authorization": f"Bearer {self.token}"}

    @task(5)
    def movies(self) -> None:
        self.client.get("/movies?page=1&page_size=8", name="/movies")

    @task(3)
    def trending(self) -> None:
        self.client.get("/movies/trending", name="/movies/trending")

    @task(2)
    def home(self) -> None:
        if self.token:
            self.client.get("/home", headers=self._auth_headers(), name="/home")

    @task(2)
    def profile(self) -> None:
        if self.token:
            self.client.get("/profile", headers=self._auth_headers(), name="/profile")

    @task(1)
    def ai_search(self) -> None:
        self.client.post(
            "/search/ai",
            json={"query": "Funny science fiction movies from the 2020s"},
            headers=self._auth_headers(),
            name="/search/ai",
        )
