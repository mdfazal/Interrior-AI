from dotenv import load_dotenv
load_dotenv()
import os
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import httpx
from io import BytesIO

app = FastAPI()

# Configure CORS – adjust the allowed origin as needed.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # your Next.js frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load your Stability API key from the environment.
API_KEY = os.getenv("STABILITY_API_KEY")
if not API_KEY:
    raise Exception("STABILITY_API_KEY not set in your environment")

# Define our features mapping with descriptive prompts.
features = {
    "color change": {
        "url": "https://api.stability.ai/v2beta/stable-image/edit/search-and-recolor",
        "data": {
            "prompt": "Change the dominant colors of the image to be more vibrant and appealing",
            "select_prompt": "main color",
            "output_format": "jpeg"
        },
        "media_type": "image/jpeg"
    },
    "refresh": {
        "url": "https://api.stability.ai/v2beta/stable-image/edit/search-and-replace",
        "data": {
            "prompt": "Refresh the design elements while preserving the layout and integrity of the scene",
            "search_prompt": "furniture",
            "output_format": "webp"
        },
        "media_type": "image/webp"
    },
    "maximize": {
        "url": "https://api.stability.ai/v2beta/stable-image/edit/outpaint",
        "data": {
            "prompt": "Expand the image by intelligently outpainting contextually appropriate elements",
            "left": 200,
            "down": 200,
            "output_format": "webp"
        },
        "media_type": "image/webp"
    },
    "redesign": {
        "url": "https://api.stability.ai/v2beta/stable-image/control/sketch",
        "data": {
            "prompt": "Redesign the room with a creative layout and innovative perspective",
            "control_strength": 0.8,
            "output_format": "webp"
        },
        "media_type": "image/webp"
    },
    "functional change": {
        "url": "https://api.stability.ai/v2beta/stable-image/control/style",
        "data": {
            "prompt": "Transform the room’s function into a new theme while keeping its structure intact",
            "output_format": "webp"
        },
        "media_type": "image/webp"
    },
    "style stealer": {
        "url": "https://api.stability.ai/v2beta/stable-image/control/style",
        "data": {
            "prompt": "Apply a distinctive artistic style to the room based on the original design",
            "output_format": "webp"
        },
        "media_type": "image/webp"
    },
    "image quality enhancer": {
        "url": "https://api.stability.ai/v2beta/stable-image/upscale/fast",
        "data": {
            "prompt": "Enhance the image’s resolution and clarity, making details crisper",
            "output_format": "webp"
        },
        "media_type": "image/webp"
    }
}

@app.post("/transform")
async def transform_image(
    image: UploadFile = File(...),
    feature: str = Form(...),
    extra_prompt: str = Form(None)
):
    if feature not in features:
        raise HTTPException(status_code=400, detail="Invalid feature selected")
    
    feature_info = features[feature]
    url = feature_info["url"]
    
    # Copy the default payload so we don’t modify the shared mapping.
    payload = feature_info["data"].copy()
    
    # Append extra prompt details if provided.
    if extra_prompt:
        base_prompt = payload.get("prompt", "")
        payload["prompt"] = f"{base_prompt}. Additional details: {extra_prompt}"
    
    image_bytes = await image.read()
    files = {
        "image": (image.filename, image_bytes, image.content_type)
    }
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Accept": "image/*"
    }
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            resp = await client.post(url, headers=headers, data=payload, files=files)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error connecting to Stability API: {str(e)}")
    
    if resp.status_code == 200:
        extension = "jpeg" if feature_info["media_type"] == "image/jpeg" else "webp"
        response_obj = StreamingResponse(BytesIO(resp.content), media_type=feature_info["media_type"])
        response_obj.headers["Content-Disposition"] = f"inline; filename=generated_{feature.replace(' ', '_')}.{extension}"
        return response_obj
    else:
        try:
            error_info = resp.json()
        except Exception:
            error_info = resp.text
        raise HTTPException(status_code=resp.status_code, detail=error_info)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8001)