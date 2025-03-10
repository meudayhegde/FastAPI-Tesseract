from fastapi import FastAPI, UploadFile, File
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import pytesseract
from PIL import Image
import io
import cv2
import numpy as np


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    # allow_origins=[os.environ.get('FRONTEND_URL')],  # Frontend origin
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)


def preprocess_image(image: Image.Image) -> Image.Image:
    """Preprocess the image for better OCR accuracy."""
    # Convert PIL image to OpenCV format
    img = np.array(image)

    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

    # Apply Otsu's thresholding (binarization)
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # Remove noise using median blur
    denoised = cv2.medianBlur(thresh, 3)

    # Convert back to PIL image
    return Image.fromarray(denoised)


@app.post('/tesseract')
async def tesseract(files: List[UploadFile] = File(...)):
    ans = {}
    for file in files:
        contents = await file.read()
        image = np.array(Image.open(io.BytesIO(contents)))

        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Apply thresholding for better OCR accuracy
        gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

        # Extract text using pytesseract
        text = pytesseract.image_to_string(gray, config="--psm 8").strip()
        
        ans[file.filename] = text

    return ans
    
if __name__ == "__main__":
    uvicorn.run(app)
