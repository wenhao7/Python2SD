# Python2SD - Generate images from your drawings within an interface
![demo](demo.gif)

## Contents
1. [Introduction](#intro)
2. [Requirements](#req)
3. [How does it work?](#how)
4. [Using the script](#using)

<a id='intro'></a>
## 1. Introduction
This is something that I did for fun while exploring Stable Diffusion. The python script creates an interface for users to draw in, relevant files can be found in this [github repo](https://github.com/wenhao7/Python2SD). The script generates images through StableDiffusion in near realtime (performance varies by hardware and model settings used). This works by sending json payloads as an API call to our generative model each time a user adds an element to the drawing.

<a id='req'></a>
## 2. Requirements
1. [Stable Diffusion WebUI by AUTOMATIC1111](https://github.com/AUTOMATIC1111/stable-diffusion-webui) with [API Mode enabled](https://github.com/AUTOMATIC1111/stable-diffusion-webui/wiki/API)
2. ControlNet extension with [Scribble Model](https://huggingface.co/lllyasviel/ControlNet-v1-1/tree/main)
3. Stable Diffusion v1.5 checkpoint of your choice

<a id='how'></a>
## 3. How does it work?
In the drawing interface rendered using `tkinter` package there are several options for the user to add elements to the drawings on the left, or edit the image prompt to use for image generation.

Each time an element is added to the drawing interface, the python script encodes the drawing and makes an API call to StableDiffusion WebUI to generate an image through txt2img with Scribble ControlNet model enabled by combining the user's prompt and the user's drawing. Scribble model augments the Stable Diffusion model with conditional inputs (i.e. our drawing) to bring our drawings to life through our chosen Stable Diffusion model.
![controlnet_archi](https://huggingface.co/lllyasviel/control_v11p_sd15_scribble/resolve/main/sd.png)

Additional settings can be editted within the WebUI or provided in the json payload. API documentations can be accessed when WebUI is running via the `/docs` endpoint which is [http://127.0.0.1:7860/docs](http://127.0.0.1:7860/docs) by default. Schema for txt2img API request can be found [here](http://127.0.0.1:7860/docs#/default/text2imgapi_sdapi_v1_txt2img_post)

My default payload json is as follows:
```
{"prompt": "", 
"seed": 3456789904, 
"negative_prompt": "", 
"batch_size": 1, 
"steps": 15, 
"cfg_scale": 7, 
"alwayson_scripts": 
    {"controlnet": 
        {"args": [{"input_image": "test", "module": "scribble_hed", "model": "control_v11p_sd15_scribble [d4ba51ff]"}]
        }
    }
}
```

Each time an image is generated it is sent back via WebUI's API and displayed on the right of the drawing interface.

<a id='using'></a>
## 4. Using the script
With WebUI server running with API mode enabled, simply execute App.py and start drawing!

If WebUI is not setup using the default url, an edit needs to be made within the python script line 75.
```
# Stablediffusion variables
self.url = "http://127.0.0.1:7860"
```
