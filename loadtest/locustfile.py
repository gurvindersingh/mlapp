from locust import HttpLocust, TaskSet
import os

def index(l):
    l.client.get("/")

def predict(l):
    img = open('keeshond.jpg', 'rb')
    l.client.post("/predict", files={'file': img})

class UserBehavior(TaskSet):
    if os.getenv("INDEX", "") == "run":
        tasks = {index: 5}
    else:
        tasks = {predict: 5}

class WebsiteUser(HttpLocust):
    task_set = UserBehavior
    min_wait = 50
    max_wait = 100
