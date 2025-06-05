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

import logging 

logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def encode_image(image_source):
    """Encode image to base64 string"""
    if isinstance(image_source, bytes):
        image = Image.open(io.BytesIO(image_source))
    else:
        image = Image.open(image_source)
    
    
    image = image.resize((1024, 1024), Image.Resampling.LANCZOS)

    # Save to bytes buffer
    buffer = io.BytesIO()
    image.save(buffer, format="JPEG")
    buffer.seek(0)
    
    # Convert to base64
    return base64.b64encode(buffer.read()).decode("utf-8")    
    
    # with open(image_path, "rb") as image_file:
    #     return base64.b64encode(image_file.read()).decode("utf-8")
  
  

model_key=""
api_gateway_url=""

langfuse_url=""
local_public_key = ""
local_secret_key = "" 

os.environ["LANGFUSE_SECRET_KEY"] = local_secret_key
os.environ["LANGFUSE_HOST"] = langfuse_url
os.environ["LANGFUSE_PUBLIC_KEY"] = local_public_key


 
# Initialize Langfuse CallbackHandler for Langchain (tracing)
langfuse_handler = CallbackHandler()

# two LLMs for the defect detection and supervisor agent 
# model_vision = "vllm-llama-3.2-vision" # "vllm-server-qwen-vision"
model_vision = "vllm-server-qwen-vision"

# model_supervisor = "vllm-llama-3.3" # "vllm-server-qwen-vision"
model_supervisor = "qwen3-vllm"
defect_detection_model = ChatOpenAI(model=model_vision, temperature=0.1, api_key=model_key, base_url=api_gateway_url)
supervisor_model = ChatOpenAI(model=model_supervisor, temperature=0.1, api_key=model_key, base_url=api_gateway_url)


defect_detection_agent = None
defect_detection_node = None

workflow = None
memory = None
graph = None

# The defect could be a cracked surface, crack, a dent, or any other visible defect. \n
# Convert the given image into RGB format using the tools provided before identifying the construction defects.
                                    
# The returned image coordinates should result in a clear image and the defective areas should be clearly visible. \n
# The returned image coordinates should result in a clear image and the defective areas should be clearly visible, preferably in the center. \n
                                    
defect_detection_system_prompt = """You are an expert in identifying construction defects location in a given image. \n
The defect could be a cracked surface, crack, a dent, or any other visible defect. \n
The defect could also be a leakage, a rust, mould, misaligned panels, or bending in the structure. \n
Ignore any other objects in the image and focus only on the construction defects. \n
Identify construction defects, and return only the image coordinates which capture all the defects in the provided image. \n
It is of Critical that you add adjacent areas of the defect while calculating the coordinates to make sure a clearly visible defect.\n
Return only one set of image coordinates that captures all of the defects in the image, And nothing else. \n
Make sure to return the coordinates in json format such as {"x": 100, "y": 140, "width": 200, "height": 300} format. \n
The json should be strictly machine readable. Do not add any details or explanations. \n
It is important that json that you generate just json and doesnot have ``` or json code block like structure.\n
Be very strict and concise about returning the json readable response only and just one set of coordinates.
"""



members = {
    "DefectDetectionAgent": "An agent that finds the defective areas in an image and return the coordinates of the defects in json format.",
    "ClassifyDefectsAgent": "A node that classifies the defects in the image using a cnn model.",  
    "CropImageAgent": "A node that crops the image to the given coordinates.",  
      
}

system_prompt = (
    "You are a highly efficient supervisor managing a collaborative conversation between specialized agents:"
    "\n{members_description}"
    "\nYour role is to:"
    "\n1. Analyze the user's request and the ongoing conversation."
    "\n2. Determine which agent is best suited to handle the next task."
    "\n3. Ensure a logical flow of information and task execution."
    "\n4. Correctly detect task completion and respond with 'FINISH', especially when rule agent has been called already. "
    "\n\tIt is critical that if an agent has been called once, do not call it again. IF it happens just go to next stage or if its the same agent go to FINISH immediately."
    "\n5. Facilitate seamless transitions between agents as needed."
    "\n6. Conclude the process by responding with 'FINISH' when all objectives are met."
    "\nRemember, each agent has unique capabilities, so choose wisely based on the current needs of the task."
)


members_description = "\n".join([f"- {k}: {v}" for k, v in members.items()])

system_prompt = system_prompt.format(members_description=members_description)

# Possible options for the supervisor
options = ["FINISH"] + list(members.keys())

# Define the supervisor's output schema
class RouteResponse(BaseModel):
    """
    The supervisor's response to the user's request.
    """
    next: Literal["FINISH", "DefectDetectionAgent", "ClassifyDefectsAgent", "CropImageAgent"]

# Supervisor Prompt
supervisor_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="messages"),
        (
            "system",
            "Based on the conversation, who should act next? Choose one of: {options}",
        ),
    ]
).partial(options=str(options), members=", ".join([f"{k}: {v}" for k, v in members.items()]))


async def supervisor_agent(state):
    logger.info("**************** Supervisor Node ****************")
    supervisor_chain = supervisor_prompt | supervisor_model.with_structured_output(RouteResponse)
    filtered_messages = []
    for message in state["messages"]:
        if ( isinstance(message, HumanMessage) or isinstance(message, AIMessage) )and isinstance(message.content, list):
            text_content = []
            for item in message.content:
                if isinstance(item, dict) and "type" in item and item["type"] == "text":
                    text_content.append(item)
            if text_content:
                # Create a new message with only text content
                filtered_message = HumanMessage(content=text_content)
                filtered_messages.append(filtered_message)
        else:
            # Keep messages without structured content
            filtered_messages.append(message)
    result = supervisor_chain.invoke({"messages": filtered_messages})
    return {
        "messages": state["messages"] + [AIMessage(content=f"I'll route to {result.next}", name="SupervisorAgent")],
        "next": result.next
    }

    # return supervisor_chain.invoke(state)



class AgentState(TypedDict):
    messages: Annotated[Sequence[HumanMessage], operator.add]
    next: str



# Helper Function for Agent Nodes
    
async def agent_node(state, agent, name):
    filtered_messages = state["messages"]
    logger.info("**************** Agent Node" + name + " ****************")
    
    result = await agent.ainvoke({"messages": filtered_messages})
    # Add the agent's response to the conversation
    return {
        "messages": [AIMessage(content=result["messages"][-1].content, name=name)]
    }

    



def clean_json_string(text):
    """
    Remove code block markers and other formatting from a JSON string
    
    Args:
        text: String that may contain JSON with code block markers
        
    Returns:
        Cleaned JSON string
    """
    import re
    
    # Remove markdown code block markers
    text = re.sub(r'```json', '', text)
    text = re.sub(r'```', '', text)
    
    # Remove any leading/trailing whitespace
    text = text.strip()
    
    return text

@observe
async def crop_image_node(state: AgentState):
    logger.info("**************** Crop Image Node ****************")
    image_coordinates_to_crop = state["messages"][-2].content
    image_coordinates_to_crop = clean_json_string(image_coordinates_to_crop)
    logger.info("----- Image Coorodinates -----")
    logger.info(image_coordinates_to_crop)
    logger.info("----- END Image Coordinates -----")

    image_content = state["messages"][0].content
    # logger.info("----- Image Content -----")
    # logger.info(image_content)
    # logger.info("----- END Image Content -----")

    base64_image = None
    # If image_content is a structured message with multiple parts
    if isinstance(image_content, list):
        # Look for image content in the message

        for item in image_content:
            if isinstance(item, dict) and item.get("type") == "image_url":
                # Extract base64 data from URL format like "data:image/png;base64,..."
                image_url = item.get("image_url", {}).get("url", "")
                if image_url.startswith("data:image/"):
                    base64_image = image_url.split("base64,")[1]
                    break
    else:
        logger.info("Image content not found")


    import json
    coordinates = json.loads(image_coordinates_to_crop)
    
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


    return {
        "messages": [AIMessage(
            content=[
                {"type": "text", "text": "Here is the cropped image of the defect:"},
                {
                    "type": "image_url", 
                    "image_url": {"url": f"data:image/jpeg;base64,{cropped_base64}"}
                }
            ],
            name="CropImageAgent"
        )]
    }
    
@observe
async def classify_defects_conv_node(state: AgentState):
    logger.info("**************** Classify Defects Node ****************")
    cropped_image_content = state["messages"][-2].content
    
    
    # If image_content is a structured message with multiple parts
    if isinstance(cropped_image_content, list):
        # Look for image content in the message
        base64_image = None
        for item in cropped_image_content:
            if isinstance(item, dict) and item.get("type") == "image_url":
                # Extract base64 data from URL format like "data:image/png;base64,..."
                image_url = item.get("image_url", {}).get("url", "")
                if image_url.startswith("data:image/"):
                    base64_image = image_url.split("base64,")[1]
                    break
    else:
        # If the content is already a base64 string
        base64_image = cropped_image_content

    
    if not base64_image:
        return {"messages": [AIMessage(content="No image found in the message", name="ClassifyDefectsAgent")]}
    
    payload = {
        "image": base64_image
    }
    
    response = requests.post(
        "http://localhost:9090/api/classify",  # Change URL as needed
        json=payload,
        headers={"Content-Type": "application/json"}
        )
    
    # Check the response
    if response.status_code == 200:
        result = response.json()
        logger.info(f"Classification result: {result}")
        defect_category = result.get("defect_category", "Unknown")
        return {"messages": [AIMessage(content=f"Detected category: {defect_category}", name="ClassifyDefectsAgent")]}
    
    else:
        logger.info(f"Error: {response.status_code}")
        logger.info(response.text)    
        return {"messages": [AIMessage(content=f"No category Detected", name="ClassifyDefectsAgent")]}  





        
app = FastAPI(title="LangGraph Agentic Demo")


# @app.get("/api/classify_defects")
# async def classify_defects():

        
@app.post("/api/classify_defects")
async def classify_defects(image_file: UploadFile = File(...)):    

    defect_detection_agent = create_react_agent(defect_detection_model, tools=[], prompt=defect_detection_system_prompt).with_config({"callbacks": [langfuse_handler], "recursion_limit": 2,})
    defect_detection_node = functools.partial(agent_node, agent=defect_detection_agent, name="DefectDetectionAgent")
    
    # classify_defect_ai_node = functools.partial(agent_node, agent=defect_detection_agent, name="ClassifyDefectsAgent")

    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("DefectDetectionAgent", defect_detection_node)
    workflow.add_node("ClassifyDefectsAgent", classify_defects_conv_node)
    # workflow.add_node("ClassifyDefectsAgent", classify_defect_ai_node)
    workflow.add_node("CropImageAgent", crop_image_node)

    workflow.add_node("Supervisor", supervisor_agent)


    for member in members:
        # Each agent reports back to the supervisor
        workflow.add_edge(member, "Supervisor")

    # Supervisor decides the next agent or to finish
    conditional_map = {member: member for member in members}
    conditional_map["FINISH"] = END
    workflow.add_conditional_edges("Supervisor", lambda x: x["next"], conditional_map)

    # Entry point
    workflow.add_edge(START, "Supervisor")

    # Compile the graph with memory checkpointing
    memory = MemorySaver()
    graph = workflow.compile(checkpointer=memory, debug=False)    
    logger.info(graph.get_graph().print_ascii())
    # Be sure to use different thread_ids for different runs
    import uuid
    thread_id = "defect_detection" #str(uuid.uuid4())    
    config = { "configurable": {"thread_id": thread_id},  
            "callbacks": [langfuse_handler], 
            "recursion_limit": 10,
            "run_name": f"idp_multi-agent_{thread_id}"}




    # Run the graph
    # building_image = encode_image("PIN_0841.jpg")
    image_bytes = await image_file.read()
    building_image = encode_image(image_bytes)
    
    # building_image = encode_image(request_data.image)

    building_image_prompt = """This is an image of building structure. Do the following:
                                \n1. Detect defect in the provided image and return only the coordinates of the defect..
                                \n2. Crop the image based on the coordinates of the defect.
                                \n3. Classify the defects in the cropped image and return the defect category.
                                \n4. Finish the workflow """

    building_image_user_prompt = HumanMessage(content= [
                            {
                                "type": "text",
                                "text": building_image_prompt,
                                        
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": "data:image/jpeg;base64," + building_image
                                }
                            }
                        ])    
  

    #
    
    final_result = await graph.ainvoke({"messages": [building_image_user_prompt]}, config=config)
    
     
    logger.info(final_result.get("next"))             
    logger.info(final_result.get("messages")[-2].content)
    return {
        "defect_category": final_result.get("messages")[-2].content
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok"}

if __name__ == "__main__":

    uvicorn.run("fault-detection-multi-agent:app", 
                host="0.0.0.0", port=8080, reload=True,
                log_level="info")
