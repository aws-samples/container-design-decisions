from transformers import AutoImageProcessor
from transformers import AutoModelForImageClassification
from fastapi import FastAPI
import base64
import uvicorn
import openai
import torch
import torch.multiprocessing as mp
from pydantic import BaseModel
from PIL import Image
import io
import logging , os
from langchain_openai import ChatOpenAI

from langfuse.callback import CallbackHandler
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Identify-Defects-In-Image", host="0.0.0.0", port=8100)


logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

model_key=os.environ.get("LLAMA_VISION_MODEL_KEY", "")
api_gateway_url=os.environ.get("GATEWAY_URL", "")

langfuse_url=os.environ.get("LANGFUSE_URL", "")
local_public_key = os.environ.get("LANGFUSE_PUBLIC_KEY", "")
local_secret_key = os.environ.get("LANGFUSE_SECRET_KEY", "") 

os.environ["LANGFUSE_SECRET_KEY"] = local_secret_key
os.environ["LANGFUSE_HOST"] = langfuse_url
os.environ["LANGFUSE_PUBLIC_KEY"] = local_public_key


 
# Initialize Langfuse CallbackHandler for Langchain (tracing)
langfuse_handler = CallbackHandler()

vision_model = "vllm-server-qwen-vision"
client = openai.OpenAI(
    api_key=model_key,            
    base_url=api_gateway_url 
)

defect_detection_system_prompt = """You are an expert in identifying construction defects coordinates bounding box in a given image. \n
The defect could be a cracked surface, crack, a dent, or any other visible defect. \n
The defect could also be a leakage, a rust, mould, misaligned panels, or bending in the structure. \n
Ignore any other objects in the image and focus only on the construction defects. \n
Identify construction defects, and return only the coordinates which capture all the defects in the provided image. \n
It is extremely critical that you add adjacent areas of the defect while calculating the coordinates to make sure a clearly visible defect.\n
Return only one set of image coordinates that captures all of the defects in the image, And nothing else. \n
Make sure to return the coordinates in json format such as {"x": 100, "y": 140, "width": 200, "height": 300} format. \n
The json should be strictly machine readable. Do not add any details or explanations. \n
Be very strict and concise about returning the json readable response only and just one set of coordinates.
"""

user_prompt = "This is an image of building structure. Detect defect in the provided image and return only the coordinates of the defect"

from utils import load_object

@mcp.tool(name="Identify-Defects-In-Image",
          description="Identify the defects in the given image. It expects a image_id  parameter and tool will know how to fetch the right image. and It will return the coordinates of the defects as bounding box. The coordinates should be provided in the format: {'x': int, 'y': int, 'width': int, 'height': int}.",)
async def identify_defects(image_id: str) -> str:
    logger.info("**************** Identify Defects Tool ****************")
    base64_image = load_object(image_id)
    response = client.chat.completions.create(
            model=vision_model,
            messages=[
                {
                "role": "system",
                "content": defect_detection_system_prompt , 
                },
                {
                    "role": "user",
                    "content": [
                    {
                                "type": "text",
                                "text": user_prompt,
                                        
                            },                        
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ]
        )    


    document_content = f"\n Extracted coordinates in json:\n {response.choices[0].message.content}"
    print(document_content)
    return response.choices[0].message.content


if __name__ == "__main__":
    mcp.run(transport="sse")
    
