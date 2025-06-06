# https://python.langchain.com/docs/how_to/migrate_agent/
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain_mcp_adapters.tools import load_mcp_tools
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from contextlib import asynccontextmanager
from typing import Annotated, Literal, Sequence
from pydantic import BaseModel
import uvicorn
import requests
import operator
import traceback
from langchain.tools.base import StructuredTool
import functools
from langgraph.graph.message import add_messages
import os
from mcp import ClientSession
from langfuse.callback import CallbackHandler
import asyncio
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import AIMessage, HumanMessage

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langchain.tools import Tool

from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langgraph.graph import StateGraph, END
from typing import TypedDict, List, Dict, Any

from langgraph.graph import StateGraph, START
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import tools_condition, ToolNode


from langgraph.graph import MessagesState
from langchain_core.messages import SystemMessage
import base64
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate

from langgraph.checkpoint.memory import MemorySaver

from transformers import AutoImageProcessor
from transformers import AutoModelForImageClassification, TrainingArguments, Trainer
import base64
import io
from fastapi import FastAPI, Body, Request, Response, UploadFile, File
from pydantic import BaseModel
from typing import Optional
from PIL import Image
import torch
from fastapi import FastAPI
from langfuse.decorators import langfuse_context, observe
from io import BytesIO
from PIL import Image

import secrets


import logging 

logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def generate_256_bit_hex_key():
    """
    Generates a cryptographically strong 256-bit random key 
    and returns it as a hexadecimal string.
    """
    # 256 bits is 32 bytes (256 / 8 = 32)
    key_bytes = secrets.token_bytes(32)
    # Convert bytes to a hexadecimal string
    key_hex = key_bytes.hex()
    return key_hex

def encode_image(image_source):
    """Encode image to base64 string"""
    if isinstance(image_source, bytes):
        image = Image.open(io.BytesIO(image_source))
    else:
        image = Image.open(image_source)
    
    
    #image = image.resize((1920, 1080), Image.Resampling.LANCZOS)
    image = image.resize((2400, 1600), Image.Resampling.LANCZOS)
    # Save to bytes buffer
    buffer = io.BytesIO()
    image.save(buffer, format="JPEG")
    buffer.seek(0)
    
    # Convert to base64
    return base64.b64encode(buffer.read()).decode("utf-8")    
    
    # with open(image_path, "rb") as image_file:
    #     return base64.b64encode(image_file.read()).decode("utf-8")
  
  

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


react_model_name = "qwen3-vllm"


react_model = ChatOpenAI(model=react_model_name, temperature=0.1, 
                         api_key=model_key, base_url=api_gateway_url,
                         timeout=360,)



workflow = None
memory = None
graph = None


# You are not going to process the image directly, but you will use the tools provided to analyze and process the image. 

system_prompt = (
    """You are a helpful AI assistant for structural inspection. 
    
    Your task is to identify construction defects and recommend mitigation action, based on an image provided by the user, by using the tools provided. 
    
    Follow these instructions:
    1. First, you need to process the image to identify the defect area, and return the coordinates of the defect area using the tools provided.  
    2. Then using the defect area coordinates, crop the image to focus on the defect area using the tools provided.
    3. Then analyze the processed image and classify defect type into one of the categories of 'A','B','C' and 'D' using the tools provided. 
    4. Present the defect type category to the user. 
    
    You are given a set of MCP tools to perform the task.     
    It is critical that you use the tools to process the image and analyze it. 
    You just need to pass the image_id to the tools from the user request, the tools will know where to fetch image from.

    1. Use 'Crop-Image' and 'Identify-Defects-In-Image' for image pre-processing.
    2. Use 'Classify-Defects' tool for defect classification. 
    """
)



        
app = FastAPI(title="LangGraph Agentic Demo")




mcp_server_params =     {
        "Crop-Image": {
            "url": "http://localhost:8200/sse",  # If already running
            "transport": "sse",
        },
        "Identify-Defects-In-Image": {
            "url": "http://localhost:8100/sse",  # If already running
            "transport": "sse",
        },
        "Classify-Defects": {
            "url": "http://localhost:8000/sse",  # If already running
            "transport": "sse",
        }
        
    }

from utils import store_object
        
@app.post("/api/classify_defects")
async def classify_defects(image_file: UploadFile = File(...)):    

    image_bytes = await image_file.read()
    building_image = encode_image(image_bytes)
    memory = MemorySaver()

    building_image_id = generate_256_bit_hex_key()
    store_object(building_image, building_image_id)
    

    
    async with MultiServerMCPClient(mcp_server_params) as client:
        original_tools = client.get_tools()
        logger.info(f"Available tools: {original_tools}")

        graph =create_react_agent(react_model, 
                                  checkpointer=memory,
                                  prompt=SystemMessage(content=system_prompt),
                                  tools=original_tools, debug=True)
        graph = graph.with_config({
                "run_name": "defect_detection_agent",
                "callbacks": [langfuse_handler],
                "recursion_limit": 25,
                "configurable": {"thread_id": "defect_detection"},
                
                
            })        
        user_prompt = HumanMessage(content= [
                                {
                                    "type": "text",
                                    "text":"\n {'image_id' : '" + building_image_id + "'}",
                                    # "text": system_prompt + "\n The image is:" + "data:image/png;base64," + building_image,
                                            
                                },
                                # {
                                #     "type": "image_url",
                                #     "image_url": {
                                #         "url": "data:image/png;base64," + building_image
                                #     }
                                # }
                            ])    


        

        final_result = await graph.ainvoke({"messages": [user_prompt]}, debug=True)
        # async for s in graph.astream({"messages": [user_prompt]}, stream_mode="values"):
        #     message = s["messages"][-1]
        #     if isinstance(message, tuple):
        #         print(message)
        #     else:
        #         message.pretty_print()
                
        #     if isinstance(message, AIMessage):
        #         final_message = message.content
        #         print("Final message:", final_message)          
     
        return {
            "defect_category": final_result.get("messages")[-2].content
        }




  
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok"}

if __name__ == "__main__":

    uvicorn.run("fault-detection-react-agent:app", 
                host="0.0.0.0", port=8080, reload=True,
                log_level="info")
