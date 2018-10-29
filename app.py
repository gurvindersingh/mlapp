from typing import Optional

from prometheus_client import Histogram

from molten import (App, Route, Settings, HTTP_401, HTTPError, Header,
     annotate, ResponseRendererMiddleware
)
from molten.openapi import OpenAPIHandler, OpenAPIUIHandler, Metadata, HTTPSecurityScheme
from molten.contrib.toml_settings import TOMLSettingsComponent
from molten.contrib.prometheus import expose_metrics, prometheus_middleware

def auth_middleware(handler):
    def middleware(authorization: Optional[Header]):
        if authorization and authorization[len("Bearer "):] == "testing" or getattr(handler, "no_auth", False):
            return handler()
        raise HTTPError(HTTP_401, {"error": "bad credentials"})
    return middleware


get_schema = OpenAPIHandler(
    metadata=Metadata(
        title='ML App',
        description='A test ML application',
        version='0.0.0'
    ),
    security_schemes=[
        HTTPSecurityScheme("Bearer Auth", "bearer")
    ],
    default_security_scheme="Bearer Auth"
)

get_docs = OpenAPIUIHandler()

prediction_hist = Histogram('prediction', 'Prediction made by model', ['model'])

get_schema = annotate(no_auth=True)(get_schema)
get_docs = annotate(no_auth=True)(get_docs)

def index(settings: Settings) -> dict:
    return settings


def predict(name: str, prediction: float) -> str:
    prediction_hist.labels(name).observe(prediction)
    return f"Model {name} made prediction: {prediction}!"


app = App(
    components=[TOMLSettingsComponent()],
    middleware=[
        prometheus_middleware,
        ResponseRendererMiddleware(),
        auth_middleware,
    ],
    routes=[
        Route("/_docs", get_docs),
        Route("/_schema", get_schema),
        Route("/", index),
        Route("/predict/{name}/{prediction}", predict),
        Route("/metrics", expose_metrics),
    ],
)