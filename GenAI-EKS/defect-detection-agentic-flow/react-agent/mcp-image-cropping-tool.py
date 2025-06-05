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
from io import BytesIO
import logging 
from mcp.server.fastmcp import FastMCP
import logging 

logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

mcp = FastMCP("Crop-Image", host="0.0.0.0", port=8200)



from utils import load_object, store_object
import json

@mcp.tool(name="Crop-Image",
          description="Crop a given image to the specified coordinates. The tool will fetch the image using the image_id parameter. The coordinates should be provided in the format: {'x': int, 'y': int, 'width': int, 'height': int}. The tool will also store the cropped image in central store and return the cropped_image_id",)
async def crop_image_node(image_id: str, image_coordinates_to_crop: dict) -> str:
    base64_image = load_object(image_id)
    logger.info("**************** Crop Image Tool ****************")

    # If somehow a dict is passed, use it directly
    coordinates = image_coordinates_to_crop

    logger.info("----- Image Coordinates -----")
    logger.info(coordinates)
    logger.info("----- END Image Coordinates -----")


    
    
    image_bytes = base64.b64decode(base64_image)
    image = Image.open(io.BytesIO(image_bytes))    
    x =  coordinates["x"]
    y = coordinates["y"]
    cropped_image = image.crop((x, y,  x + coordinates["width"], y + coordinates["height"]))
    cropped_image.save("cropped_image.jpg")
    
    output = BytesIO()
    cropped_image.save(output, format="JPEG")
    output.seek(0)    
    
    cropped_base64 = base64.b64encode(output.getvalue()).decode("utf-8")

    cropped_image_id = image_id + "-cropped"
    store_object(cropped_base64, cropped_image_id)

    return f"cropped_image_id is {cropped_image_id}"
    
    
if __name__ == "__main__":
    mcp.run(transport="sse")
    