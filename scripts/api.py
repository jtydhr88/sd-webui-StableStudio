import numpy as np
from fastapi import FastAPI, Body
from fastapi.exceptions import HTTPException
from PIL import Image
import os
import gradio as gr

from modules.api.models import *
from modules.api import api
import glob
import base64
from pydantic import BaseModel


def get_root_path():
    path = os.path.dirname(os.path.realpath(__file__))
    path = os.path.dirname(path)
    path = os.path.dirname(path)
    path = os.path.dirname(path)

    return path


class GetGeneratedImagesRequest(BaseModel):
    limit: int = 10


def StableStudio_api(_: gr.Blocks, app: FastAPI):
    @app.get("/StableStudio/check-extension-installed")
    async def check_extension_installed(extension_name: str):
        extension_path = os.path.join(get_root_path(), "extensions", extension_name)

        installed = 0

        if os.path.exists(extension_path):
            installed = 1

        return {
            "extension_path": extension_path,
            "installed": installed
        }

    @app.post("/StableStudio/get-generated-images")
    async def get_generated_images(request: GetGeneratedImagesRequest):
        outputs_path = os.path.join(get_root_path(), "outputs")

        txt2img_folder = os.path.join(outputs_path, 'txt2img-images', '**')
        img2img_folder = os.path.join(outputs_path, 'img2img-images', '**')

        files = glob.glob(txt2img_folder, recursive=True) + glob.glob(img2img_folder, recursive=True)

        files = [f for f in files if os.path.isfile(f)]

        files.sort(key=os.path.getctime, reverse=True)

        files = files[:request.limit]

        return_values = []

        for file in files:
            with open(file, "rb") as f:
                img = Image.open(f)
                width, height = img.size

                encoded_content = api.encode_pil_to_base64(img)

                return_value = {
                    "image_name": os.path.basename(file),
                    "create_date": os.path.getctime(file),
                    "content": encoded_content,
                    "width": width,
                    "height": height
                }

                return_values.append(return_value)

        return return_values


try:
    import modules.script_callbacks as script_callbacks

    script_callbacks.on_app_started(StableStudio_api)
except:
    pass
