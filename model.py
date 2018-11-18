import base64
import json
import logging
import numpy as np
import os
import PIL
import sys
import torch

from io import BytesIO
from pathlib import Path
from urllib.parse import unquote
import urllib.request
from urllib.error import HTTPError

from molten import schema, UploadedFile
from molten.validation import Field

from fastai.vision import (
    create_cnn,
    get_transforms,
    Image,
    ImageDataBunch,
    imagenet_stats,
    models,
    open_image,
    pil2tensor
)

from config import CONFIG

@schema
class ModelData():
    file: UploadedFile


@schema
class FeedbackData():
    file: UploadedFile
    predicted: str = Field(choices=CONFIG[CONFIG['model_name']]['classes'])
    expected: str = Field(choices=CONFIG[CONFIG['model_name']]['classes'])

FEEDBACK_DIR = 'feedback'
FEEDBACK_SEP = '__'

def path_to(*segments):
    return os.path.join(os.path.abspath(os.path.dirname(__file__)), *segments)

def load():

    path = Path('.')
    global model
    global learn
    global classes
    model = CONFIG['model_name']
    # Check if we need to download Model file
    if CONFIG[model]['url'] != "":
        try:
            logging.info(f"Downloading model file from: {CONFIG[model]['url']}")
            urllib.request.urlretrieve(CONFIG[model]['url'], f"models/{model}.pth")
            logging.info(f"Downloaded model file and stored at path: models/{model}.pth")
        except HTTPError as e:
            logging.critical(f"Failed in downloading file from: {CONFIG[model]['url']}, Exception: '{e}'")
            sys.exit(4)

    init_data = ImageDataBunch.single_from_classes(
                                    path, CONFIG[model]['classes'], tfms=get_transforms(),
                                    size=CONFIG[model]['size']
                                ).normalize(imagenet_stats)
    classes = CONFIG[model]['classes']
    logging.info(f"Loading model: {CONFIG['model_name']}, architecture: {CONFIG[model]['arch']}, file: models/{model}.pth")
    learn = create_cnn(init_data, eval(f"models.{CONFIG[model]['arch']}"))
    learn.load(model, device=CONFIG[model]['device'])

    # Create direcotry to get feedback for this model
    Path.mkdir(Path(path_to(FEEDBACK_DIR, model)), parents=True, exist_ok=True)

def predict(data):
    if data is None or data.file is None:
        return ''
    img = open_image(data.file)
    pclass, idx, outputs = learn.predict(img)
    outputs = torch.nn.functional.softmax(np.log(outputs), dim=0).tolist()
    logging.debug(f"Predicted class {pclass}. Predictions:  {sorted(zip(classes, outputs), key=lambda o: o[1], reverse=True)}")
    return {"predictions": {
        pclass: outputs[idx]
    }}

def feedback(data):
    if data is None or data.file is None:
        return ''
    _, ext = os.path.splitext(data.file.filename)
    data.file.save(path_to(FEEDBACK_DIR, model, data.predicted+FEEDBACK_SEP+data.expected+ext))
    return {"success": True}
