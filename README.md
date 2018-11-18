# MLapp

A web application to serve model based on Fastai v1 library. Application is based on [Molten Framework](https://moltenframework.com/) due to it's inbuild support for modern tooling: [Swagger](https://swagger.io/), [OpenAPI](https://www.openapis.org/), [Prometheus](https://prometheus.io/) etc.

## Motivation

I wanted to have an application which allow me to serve ML models in real production settings. Application should provide:

* Versioned APIs
* Metrics (prometheus)
* Ablility to run different version of models without unnecassary code changes
* User friendly API documentations
* Input data validation
* Inference device flexibility (CPU or GPU)
* Scale up or down instances based on incoming traffic

So that I can focus on my ML model improvment and don't need to bother about how to serve the model in produciton.

## Design

Application design is very simple. `app.py` sets up the route and required methods to get data in and out. `app.py` validates data according to schema descibed in `model.py` file using Molten framework. This application provides a simple CNN model which was described in Lesson 1 of [Fast v1](https://github.com/fastai/fastai/) course.

```
/ -> Returns health information and serve as liveness check for application
/_docs -> Serves Swagger UI to provide API docs and user friendly API testing
/_schema -> json formatted API spec in OpenAPI standard
/metrics -> Endpoint to scrape metrics by Prometheus
/v1alpha1/predict -> Receives end user data to make prediction on
/v1alpha1/feedback -> User can provide feedback on prediction if there was any errors
```

versions + model schema + config

## Metrics

Prometheus + Grafana

## Deployment

Kubernetes
traffic shifting etc

## Load testing

## TODO

* Add support for ONNX