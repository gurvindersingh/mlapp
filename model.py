import base64
import json
from io import BytesIO
import logging
from pathlib import Path
import PIL
import sys
import torch
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

def load(config):

    path = Path('.')
    model = config['model_name']
    # Check if we need to download Model file
    if config['model_url'] != "":
        try:
            logging.info(f"Downloading model file from: {config['model_url']}")
            urllib.request.urlretrieve(config['model_url'], f"models/{config[model]['modelfile']}")
            logging.info(f"Downloaded model file and stored at path: models/{config[model]['modelfile']}")
        except HTTPError as e:
            logging.critical(f"Failed in downloading file from: {config['model_url']}, Exception: '{e}'")
            sys.exit(4)

    init_data = ImageDataBunch.single_from_classes(
                                    path, config[model]['classes'], tfms=get_transforms(),
                                    size=config[model]['size']
                                ).normalize(imagenet_stats)
    global learn
    global classes
    classes = config[model]['classes']
    logging.info(f"Loading model: {config['model_name']}, architecture: {config[model]['arch']}, file: models/{config[model]['modelfile']}")
    learn = create_cnn(init_data, eval(f"models.{config[model]['arch']}"))
    learn.model.load_state_dict(torch.load(f"models/{config[model]['modelfile']}", map_location='cpu'))

def predict(data):
    if data is None or data.file is None:
        return ''
    img = open_image(data.file)
    pclass, _, outputs = learn.predict(img)
    logging.debug(f"Predicted class {pclass}. Outputs: {outputs}, Classes: {classes}")
    return {"prediction": pclass}