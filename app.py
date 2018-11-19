import json
import sys
import time
import logging
import os
from humanfriendly import format_timespan
from typing import Optional
from wsgicors import CORS

from molten import (
    App, Route, Settings, HTTP_401, HTTPError, Header,
    annotate, ResponseRendererMiddleware, Response, JSONRenderer,
    JSONParser,MultiPartParser
)
from molten.openapi import OpenAPIHandler, OpenAPIUIHandler, Metadata, HTTPSecurityScheme
from molten.contrib.prometheus import expose_metrics, prometheus_middleware
from molten.contrib.request_id import RequestIdMiddleware

from model import ModelData, FeedbackData
import model
from logger import setup_logging
from config import CONFIG

# Application Version
VERSION='v0.1.0'

def auth_middleware(handler):
    """
    Authentication Middleware to check for
    Bearer token header
    """
    def middleware(authorization: Optional[Header]):
        if authorization and authorization[len("Bearer "):] == CONFIG['token'] or getattr(handler, "no_auth", False):
            return handler()
        raise HTTPError(HTTP_401, {"error": "bad credentials"})
    return middleware

# Add OpenAPI and Swaager support to our APIs
get_schema = OpenAPIHandler(
    metadata=Metadata(
        title='ML app',
        description='A test ML application',
        version=VERSION
    ),
)

# Initialize objects
start_time = time.time()
get_docs = OpenAPIUIHandler()
setup_logging()

# Annotate these objects to be accessible without authentication
get_schema = annotate(no_auth=True)(get_schema)
get_docs = annotate(no_auth=True)(get_docs)

def health() -> str:
    """
    Setup root to return application status and serve as health check or readiness endpoint
    Kubernetes or similar resource managers can start service when it replied 200 OK back
    and restart in case of failure
    """
    return {"version": VERSION,
            "uptime": format_timespan(time.time() - start_time)
            }

def predict(data: ModelData) -> str:
    """
    Pass the request data as ModelData object,
    as this can be customised in the model.py file to adapt based
    on deployed model to make predictions

    Parameters:
      data: Parse the request body data based on your model schema and
        pass this to predict method to make prediction
    """
    return model.predict(data)


def feedback(data: FeedbackData) -> str:
    """
    Pass the request data as FeedbackData object,
    as this can be customised in the model.py file to adapt based
    on deployed model to make predictions

    Parameters:
      data: Parse the request body data based on your model schema and
        pass this to predict method to make prediction
    """
    return model.feedback(data)

# Load our pre trained model
model.load()
logging.info(f"Loaded model: {CONFIG['model_name']}")

# Setup the list of middlewares to be enabled
middlewares = [prometheus_middleware, RequestIdMiddleware(), ResponseRendererMiddleware()]

# If token is not empty setup the authentication middleware as well openAPI config
if CONFIG['token'] != "":
    middlewares.append(auth_middleware)
    get_schema.security_schemes = [HTTPSecurityScheme("Bearer Auth", "bearer")]
    get_schema.default_security_scheme="Bearer Auth"

# Initialize the application with all the required routes and middlewares
app = App(
    middleware=middlewares,
    routes=[
        Route("/_docs", get_docs),
        Route("/_schema", get_schema),
        Route("/metrics", expose_metrics),
        Route("/", health),
        Route("/v1/predict", predict, method="POST"),
        Route("/v1/feedback", feedback, method="POST"),
    ],
    parsers=[
        JSONParser(),
        MultiPartParser(),
    ],
    renderers=[JSONRenderer()]
)

# If running in production, setup CORS for our application
if os.getenv("ENVIRONMENT") == "production":
    app = CORS(app, headers="*", methods="*", origin="*", maxage="86400")