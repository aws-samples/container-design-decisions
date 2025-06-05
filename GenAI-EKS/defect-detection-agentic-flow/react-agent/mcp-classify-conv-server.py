from transformers import AutoImageProcessor
from transformers import AutoModelForImageClassification
from fastapi import FastAPI
import base64
import uvicorn
import torch
import torch.multiprocessing as mp
from pydantic import BaseModel
from PIL import Image
import io
import logging 


from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Classify-Defects", host="0.0.0.0", port=8000)


logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

FT_MODEL_PATH = ""

labels_names = {
    0: "A",
    1: "B",
    2: "C",
    3: "D" 
}

labels = list(labels_names.values())
label2id, id2label = dict(), dict()

for i, label in enumerate(labels):
    label2id[label] = str(i)
    id2label[str(i)] = label

# Set device based on availability
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
logger.info(f"Using device: {device}")

try:
    image_processor=AutoImageProcessor.from_pretrained(FT_MODEL_PATH)
    inference_model = AutoModelForImageClassification.from_pretrained(
        FT_MODEL_PATH,
        num_labels=len(labels),
        id2label=id2label,
        label2id=label2id,
    )
    inference_model = inference_model.to(device)
    inference_model.eval()
    logger.info("Model loaded successfully.")
except Exception as e:
    logger.error(f"Error loading model: {e}")
    raise


import threading
model_lock = threading.Lock()


from utils import load_object

@mcp.tool(name="Classify-Defects",
          description="Classify defects in a given image. The tool will fetch the correct image using the cropped_image_id parameter. And returns the defect category as a string.")
async def classify_defects(cropped_image_id: str) -> str:
    """Classify defects in the given image. It expects a base64 encoded image string. It will return the defect category as a string."""
    logger.info("**************** Classify Defects Tool ****************")
    cropped_image_base64 = load_object(cropped_image_id)
    image_bytes = base64.b64decode(cropped_image_base64)
    image = Image.open(io.BytesIO(image_bytes))
    image.save("classify_cropped_image.jpg")

    # classification
    encoding = image_processor(image.convert("RGB"), return_tensors="pt")
    encoding_on_device = {k: v.to(device) for k, v in encoding.items()}    

    with model_lock:
        with torch.no_grad():
            outputs=inference_model(**encoding_on_device)
            logits=outputs.logits

    predicted_class_idx=logits.argmax(-1).item()
    defect_category = "MaterialDrop_" + id2label[str(predicted_class_idx)]
    print("Detected category:",defect_category)

    return f"defect_category is {defect_category}"


if __name__ == "__main__":
    mcp.run(transport="sse")
    
