# -*- coding: utf-8 -*-
"""Fair-compute.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1bh6asl_VA5_XQjeaD0UeS3mqccpltCqZ
"""

import gradio as gr
import aiohttp
import asyncio
import base64
import numpy as np
import json
from PIL import Image
import io


# Function to convert a NumPy array to a base64 string
def numpy_image_to_base64(numpy_image):
    im = Image.fromarray(numpy_image.astype("uint8"), "RGB")
    rawBytes = io.BytesIO()
    im.save(rawBytes, "JPEG")
    rawBytes.seek(0)
    img_base64 = base64.b64encode(rawBytes.read()).decode('utf-8')
    return img_base64



async def fetch_prediction(prompt, numpy_image):
    # Convert the NumPy array image to base64, if image is provided
    encoded_image = numpy_image_to_base64(numpy_image) if numpy_image is not None else None

    # Your API endpoint and payload
    url = "http://8.12.5.48:11434/api/generate"
    data = json.dumps({
        "model": "llava:34b-v1.6",
        "prompt":  "You are an expert doctor. Look at the image carefully and prescribe accurately",
        "stream":True,
        "images": [encoded_image] if encoded_image else [],
    })
    headers = {'Content-Type': 'application/json'}

    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.post(url, data=data) as response:
            return await response.text()


def get_prediction(prompt, numpy_image=None):
    response_json_str = asyncio.run(fetch_prediction(prompt, numpy_image))

    response_lines = response_json_str.strip().split('\n')

    #Convert the output returned by the model into a presentable format

    full_response = ''

    for line in response_lines:
        try:
            response_obj = json.loads(line)

            full_response += response_obj.get("response", "")
        except json.JSONDecodeError:
            print(f"Error decoding JSON: {line}")
            continue

    return full_response


iface = gr.Interface(fn=get_prediction,
                     inputs=[ gr.Image(label="Upload Image or Capture from Webcam using the webcam icon", type="numpy")],
                     outputs=[gr.Text(label="Model Response")],
                     title="DocuBot: Your AI Medical Advisor",
                     description="Upload an image and/or enter a text prompt to receive prescriptions from AI doctor.")


iface.dependencies[0]["show progress"]="hidden"
iface.launch()
