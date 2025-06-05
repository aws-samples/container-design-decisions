# https://python.langchain.com/docs/how_to/migrate_agent/
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain_mcp_adapters.tools import load_mcp_tools
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, BackgroundTasks, HTTPException, Query
import os
from mcp import ClientSession
from langfuse.callback import CallbackHandler
import asyncio
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import AIMessage, HumanMessage




local_secret_key = os.environ["LANGFUSE_SECRET_KEY"]
# os.environ["LANGFUSE_HOST"] = "http://localhost:3000"
local_public_key = os.environ["LANGFUSE_PUBLIC_KEY"] 

from langfuse.callback import CallbackHandler
 
# Initialize Langfuse CallbackHandler for Langchain (tracing)
langfuse_handler = CallbackHandler()


# Configure LLM
llm_model = "vllm-llama-3.2-vision"
llm_model_url = "http://litellm:4000"
llm_model_key = os.environ["LLAMA_VISION_MODEL_KEY"]

model = ChatOpenAI(
    model=llm_model, 
    temperature=0, 
    max_tokens=1500, 
    api_key=llm_model_key, 
    base_url=llm_model_url
)




fruit_server_params =     {
        "fruit_price_services": {
            "url": "http://mcp-fruit-services:8000/sse",  # If already running
            "transport": "sse",
        }
    }

server_params =     {
        "weather_services": {
            # make sure you start your weather server on port 8000
            "url": "http://mcp-weather:8000/sse",
            "transport": "sse",
        },
        # "fruit_price_services": {
        #     "url": "http://localhost:7000/sse",  # If already running
        #     "transport": "sse",
        # }
    }


def get_mcp_servers():
    """
    Discover MCP services from Kubernetes API based on annotations.
    Returns a dictionary suitable for MultiServerMCPClient configuration.
    
    Looks for services with annotation: mcp.enabled=true
    Each service should also have annotations:
    - mcp.service-name - The name for the MCP service
    """
    raise NotImplementedError("MCP Kubernetes service discovery not implemented yet.")   
 
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate



# Global variables to store MCP client and agent executor
# mcp_session = None
# agent_executor = None
# client = None
# agent = None

# Initialize the MCP client and agent on startup
@asynccontextmanager
async def lifespan(app: FastAPI):

    # global  client
    
    # Start MCP client
    try:
        async with MultiServerMCPClient(server_params) as client:
            tools = client.get_tools()
            
            print("Total tools loaded:", len(tools))
            for tool in tools:
                print("Tool:", tool.name)
                print("Tool description:", tool.description)
                
            
            # agent = create_tool_calling_agent(model, client.get_tools(), prompt=prompt)
            # agent =create_react_agent(model, client.get_tools())
            # agent_executor = AgentExecutor(agent=agent, tools=client.get_tools(), verbose=True)
            
            # agent_executor = agent_executor.with_config({
            #     "callbacks": [langfuse_handler],
            #     # "recursion_limit": 5,
            # })
            
            # agent = create_react_agent(
            #     model=model,
            #     tools=tools,
            #     # this goes as System MEssage. See docs
            #     prompt="You are a helpful assistant with access to various tools. Use the tools appropriately to answer the user's questions. You prefer to use tools when you can to get more accurate information.\n\n"
            # )
            
            
            # # agent_executor = agent.with_config({"run_name": "tool_agent"})
            # agent_executor = agent.with_config({
            #     "run_name": "tool_agent",
            #     "callbacks": [langfuse_handler],
            #     "recursion_limit": 3,
            # })        
            
            
            print("Agent initialized successfully with MCP tools")
            
            yield
            
            print("Shutting down agent and MCP client")

    except Exception as e:
        print(f"Error initializing agent: {str(e)}")
        


app = FastAPI(title="LangGraph Agentic Demo with MCP", lifespan=lifespan)


@app.post("/api/fruits")
async def q():

    
    async with MultiServerMCPClient(fruit_server_params) as client:
        graph =create_react_agent(model, client.get_tools(), debug=True)
        graph = graph.with_config({
                "run_name": "fruit_agent",
                "callbacks": [langfuse_handler],
                "recursion_limit": 25,
            })        
        
        inputs = {"messages": [("user", "Calculate the price in dollars for 10 kg of oranges? Use the tool calling to get the price of oranges")]}
        async for s in graph.astream(inputs, stream_mode="values"):
            message = s["messages"][-1]
            if isinstance(message, tuple):
                print(message)
            else:
                message.pretty_print()
                
            if isinstance(message, AIMessage):
                final_message = message.content
                print("Final message:", final_message)                
        return final_message
        

                

@app.post("/api/weather")
async def query():
    
    
    async with MultiServerMCPClient(server_params) as client:
        graph =create_react_agent(model, client.get_tools(), debug=True)
        graph = graph.with_config({
                "run_name": "weather_agent",
                "callbacks": [langfuse_handler],
                "recursion_limit": 25,
            })        
        
        inputs = {"messages": [("user", "What is the current temperature in Sydney city? Use the tool calling to get the weather information for location")]}
        async for s in graph.astream(inputs, stream_mode="values"):
            message = s["messages"][-1]
            if isinstance(message, tuple):
                print(message)
            else:
                message.pretty_print()
                
            if isinstance(message, AIMessage):
                final_message = message.content
                print("Final message:", final_message)                
        return final_message
    

     
            
    # agent = create_tool_calling_agent(model, client.get_tools(), prompt)            
    
    if not client:
        raise HTTPException(status_code=503, detail="MCPClient not initialized")
    

    # prompt = ChatPromptTemplate.from_messages(
    #     [
    #         ("system", "You are a helpful assistant. Use the tools to answer the user's questions."),
    #         ("human", "{input}"),
    #         # Placeholders fill up a **list** of messages
    #         ("placeholder", "{agent_scratchpad}"),
    #     ]
    # )

    # query = "What is the cost of five apples?"
    # agent = create_tool_calling_agent(model, client.get_tools(), prompt)
    # agent_executor = AgentExecutor(agent=agent, tools=client.get_tools(), verbose=True)
    # agent_executor = agent_executor.with_config({"callbacks": [langfuse_handler]})
    # result = await agent_executor.ainvoke({"input": query})    
    
    


    
    ## del            
    print(result)
    print("************ ")
        
          
        
    # Format the response
    # messages_json = []
    # for message in result["messages"]:
    #     messages_json.append({
    #         "role": message.type,
    #         "content": message.content
    #     })
    
    return {"messages": result}        
        
    

    



if __name__ == "__main__":
    uvicorn.run("langgraph-agent-react-agent:app", host="0.0.0.0", port=8080, reload=True)
    
    
