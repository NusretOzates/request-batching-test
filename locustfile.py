from locust import HttpUser, between, task


class WebsiteUser(HttpUser):
    @task
    def index(self):
        self.client.post("/predict", json={"number": "2"})
