from dotenv import load_dotenv
load_dotenv()
import os
from fastapi import FastAPI, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import requests
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

# Define features that require only a text prompt.
features = {
    "artistic": {
        "data": {
            "output_format": "jpeg"
        },
        "media_type": "image/jpeg"
    },
    "photorealistic": {
        "data": {
            "output_format": "webp"
        },
        "media_type": "image/webp"
    }
}

@app.post("/generate")
async def generate_image(
    prompt: str = Form(...),
    feature: str = Form("artistic")
):
    if feature not in features:
        raise HTTPException(status_code=400, detail="Invalid feature selected")
    
    feature_info = features[feature]
    output_format = feature_info["data"]["output_format"]

    # Use the revised snippet with the 'core' endpoint.
    response = requests.post(
        "https://api.stability.ai/v2beta/stable-image/generate/core",
        headers={
            "authorization": f"Bearer {API_KEY}",
            "accept": "image/*"
        },
        files={"none": ""},
        data={
            "prompt": prompt,
            "output_format": output_format,
        },
    )

    if response.status_code == 200:
        extension = "jpeg" if output_format == "jpeg" else "webp"
        response_obj = StreamingResponse(BytesIO(response.content), media_type=feature_info["media_type"])
        response_obj.headers["Content-Disposition"] = f"inline; filename=generated_{feature}.{extension}"
        return response_obj
    else:
        try:
            error_info = response.json()
        except Exception:
            error_info = response.text
        raise HTTPException(status_code=response.status_code, detail=error_info)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8005)