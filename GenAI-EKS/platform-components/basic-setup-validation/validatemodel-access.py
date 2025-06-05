import openai
import os

generation_model_key_var = os.getenv("LLAMA_VISION_MODEL_KEY")
if generation_model_key_var is None:
    raise ValueError("Please set the LLAMA_VISION_MODEL_KEY environment variable. You can generate the key in LiteLLM console")

client = openai.OpenAI(
    api_key=generation_model_key_var,             # pass litellm proxy key, if you're using virtual keys
    base_url="http://localhost:4000" # litellm-proxy-base url
)


response = client.chat.completions.create(
    model="vllm-llama-3.2-vision",
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "Tell me a bad joke. The joke doesnot need to be hillarious though. It can be a simple one. But make sure the joke is not too long. The joke should be short and sweet"
                }
            ]
        }
    ]
)


print(response.choices[0].message.content)