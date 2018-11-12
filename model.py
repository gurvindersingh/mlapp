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

@schema
class ModelData():
    file: UploadedFile


@schema
class FeedbackData():
    file: UploadedFile
    predicted: str
    expected: str

FEEDBACK_DIR = 'feedback'
SEP = '__'

def path_to(*segments):
    return os.path.join(os.path.abspath(os.path.dirname(__file__)), *segments)

def load(config):

    path = Path('.')
    global model
    global learn
    global classes
    model = config['model_name']
    # Check if we need to download Model file
    if config[model]['url'] != "":
        try:
            logging.info(f"Downloading model file from: {config[model]['url']}")
            urllib.request.urlretrieve(config[model]['url'], f"models/{config[model]['modelfile']}")
            logging.info(f"Downloaded model file and stored at path: models/{config[model]['modelfile']}")
        except HTTPError as e:
            logging.critical(f"Failed in downloading file from: {config[model]['url']}, Exception: '{e}'")
            sys.exit(4)

    init_data = ImageDataBunch.single_from_classes(
                                    path, config[model]['classes'], tfms=get_transforms(),
                                    size=config[model]['size']
                                ).normalize(imagenet_stats)
    classes = config[model]['classes']
    logging.info(f"Loading model: {config['model_name']}, architecture: {config[model]['arch']}, file: models/{config[model]['modelfile']}")
    learn = create_cnn(init_data, eval(f"models.{config[model]['arch']}"))
    learn.model.load_state_dict(torch.load(f"models/{config[model]['modelfile']}", map_location='cpu'))

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
    data.file.save(path_to(FEEDBACK_DIR, model, data.predicted+SEP+data.expected+ext))
    return {"success": True}
