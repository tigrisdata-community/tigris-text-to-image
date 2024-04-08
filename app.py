import io
import json
import os
import sys

import PIL
import gradio as gr
import boto3

from typing import Mapping, List, Dict

import numpy as np
from PIL import Image
from botocore.exceptions import ClientError
from dotenv import load_dotenv
from diffusers import AutoPipelineForText2Image

load_dotenv()

pipe = AutoPipelineForText2Image.from_pretrained("runwayml/stable-diffusion-v1-5")
pipe = pipe.to(os.environ['ARCH'])
# Recommended if your computer has < 64 GB of RAM
pipe.enable_attention_slicing()

svc = boto3.client(
    service_name='s3',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    endpoint_url=os.getenv('AWS_ENDPOINT_URL_S3'),
)

DEFAULT_PROMPT = "frankie with tigris"
DEFAULT_IMAGE = Image.open("Tigris-fly-sticker.png")
BUCKET_NAME = os.getenv('BUCKET_NAME')

##https://fly.storage.tigris.dev
print(BUCKET_NAME)


def gen_image(prompt: str) -> Image.Image:
    """
    tentatively flips the image
    :param prompt: prompt for image generation
    :return: generated image
    """
    if not prompt:
        prompt = DEFAULT_PROMPT
    print(f"generating images for {prompt}", file=sys.stderr)

    return pipe(prompt).images[0]


def load_image(key: str):
    """
    saves images back to the repository
    :param key:
    :return:
    """
    print(f"begin load image {key}", file=sys.stdout)
    if key == "":
        raise gr.Error("key name is empty")

    try:
        response = svc.get_object(
            Bucket=BUCKET_NAME,
            Key=key,
        )
        return Image.open(io.BytesIO(response['Body'].read())), "foo"
    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        if error_code == "NotFound":
            raise gr.Error("key " + key + "not found")
        raise gr.Error("get object error " + error_code)


def save_image(inp_img: np.ndarray, key: str, metadata: str, prompt: str):
    """
    saves images back to the repository
    :param inp_img:
    :param key:
    :param metadata:
    :param prompt:
    :return:
    """
    print(f"begin save image under {key} {metadata} {prompt}", file=sys.stdout)
    if key == "":
        raise gr.Error("key name is empty")

    metadata = {
        "prompt": prompt,
        "comment": metadata,
    }
    print(f"metadata is {json.dumps(metadata, indent=2)}", file=sys.stdout)

    byte_writer = io.BytesIO()
    inp_img.save(byte_writer, 'png')

    try:
        response = svc.put_object(
            Bucket=BUCKET_NAME,
            Key=key,
            Metadata=metadata,
            Body=byte_writer.getvalue(),
        )
        gr.Info("Image " + key + " saved in Tigris")
    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        raise gr.Error("put object error " + error_code)

    return


with gr.Blocks(
        title="Text-to-Image",
        theme=gr.themes.Default(font=["sans-serif"])) as demo:
    with gr.Row():
        with gr.Column(scale=3):
            gr.Markdown(
                """
                # Text-to-Image Generator with Hugging Face model, Fly GPUs and Tigris as storage
                """
            )
        with gr.Column(scale=0):
            pass

    with gr.Row():
        with gr.Column(scale=0):
            pass
        with gr.Column(scale=3):
            image_output = gr.Image(label="Image",
                                    show_label=False,
                                    value=DEFAULT_IMAGE,
                                    width=600,
                                    height=480,
                                    type="pil",
                                    interactive=False)
        with gr.Column(scale=2):
            gr.Markdown(
                        """
                    ## Enter a phrase
                    Generate images with huggingface [stable diffusion](https://github.com/runwayml/stable-diffusion) 
                    model.
                    """
            )
            gen_prompt_input = gr.Textbox(show_label=False, placeholder=DEFAULT_PROMPT)
            gen_btn = gr.Button("Generate image", variant="primary")

    with gr.Row():
        with gr.Column(scale=0):
            pass
        with gr.Column(scale=2):
            gr.Markdown(
                """
                ## Save your image in Tigris or load an existing image from Tigris
                """
            )
            img_key_input = gr.Textbox(
                label="", interactive=True, show_label=False,
                placeholder="key name for this image")
            metadata_input = gr.Textbox(
                label="", show_label=False,
                placeholder="Optional: Store metadata with the image")
            with gr.Row():
                save_image_btn = gr.Button("Save image", variant="primary")
                load_image_btn = gr.Button("Load image", variant="primary")
                clear = gr.ClearButton(
                    [gen_prompt_input, img_key_input, metadata_input],
                    value="Clear")
        with gr.Column(scale=2):
            pass

    # set generate button to populate the image on the right side
    gen_btn.click(fn=gen_image, inputs=gen_prompt_input, outputs=[image_output], api_name="generate_image")
    gen_prompt_input.submit(fn=gen_image, inputs=gen_prompt_input, outputs=[image_output])

    save_image_btn.click(fn=save_image,
                         inputs=[image_output, img_key_input, metadata_input, gen_prompt_input],
                         api_name="save_image")
    load_image_btn.click(fn=load_image, inputs=[img_key_input],
                         outputs=[image_output, metadata_input],
                         api_name="load_image")

demo.queue(concurrency_count=4)
demo.launch(server_name='0.0.0.0')
