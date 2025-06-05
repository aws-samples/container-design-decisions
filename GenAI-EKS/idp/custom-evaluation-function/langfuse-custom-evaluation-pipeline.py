# https://langfuse.com/docs/scores/external-evaluation-pipelines

from langfuse import Langfuse
from datetime import datetime, timedelta
import os
import math
import openai
 
BATCH_SIZE = 20
TOTAL_TRACES = 100

local_public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
local_secret_key = os.getenv("LANGFUSE_SECRET_KEY")
if local_public_key is None or local_secret_key is None:
    raise ValueError("Please set the LANGFUSE_PUBLIC_KEY and LANGFUSE_SECRET_KEY environment variables.")

langfuse = Langfuse(
    secret_key=local_secret_key,
    public_key=local_public_key,
    host="http://localhost:3000"  
)

 
now = datetime.now()
five_am_today = datetime(now.year, now.month, now.day, 17, 0)
five_am_yesterday = five_am_today - timedelta(days=10)
 
traces_batch = langfuse.fetch_traces(page=1,
                                     limit=BATCH_SIZE,
                                     from_timestamp=five_am_yesterday,
                                     to_timestamp=datetime.now()
                                   ).data
 
print(f"Traces in first batch: {len(traces_batch)}")

template_tone_eval = """
You're an expert in human emotional intelligence. You can identify with ease the
 tone in human-written text. Your task is to identify the tones present in a
 piece of <text/> with precission. Your output is a comma separated list of three
 tones. PRINT THE LIST ALONE, NOTHING ELSE.
 
<possible_tones>
neutral, confident, joyful, optimistic, friendly, urgent, analytical, respectful
</possible_tones>
 
<example_1>
Input: Citizen science plays a crucial role in research by involving everyday
people in scientific projects. This collaboration allows researchers to collect
vast amounts of data that would be impossible to gather on their own. Citizen
scientists contribute valuable observations and insights that can lead to new
discoveries and advancements in various fields. By participating in citizen
science projects, individuals can actively contribute to scientific research
and make a meaningful impact on our understanding of the world around us.
 
Output: respectful,optimistic,confident
</example_1>
 
<example_2>
Input: Bionics is a field that combines biology and engineering to create
devices that can enhance human abilities. By merging humans and machines,
bionics aims to improve quality of life for individuals with disabilities
or enhance performance for others. These technologies often mimic natural
processes in the body to create seamless integration. Overall, bionics holds
great potential for revolutionizing healthcare and technology in the future.
 
Output: optimistic,confident,analytical
</example_2>
 
<example_3>
Input: Social media can have both positive and negative impacts on mental
health. On the positive side, it can help people connect, share experiences,
and find support. However, excessive use of social media can also lead to
feelings of inadequacy, loneliness, and anxiety. It's important to find a
balance and be mindful of how social media affects your mental well-being.
Remember, it's okay to take breaks and prioritize your mental health.
 
Output: friendly,neutral,respectful
</example_3>
 
<text>
{text}
</text>
"""

def tone_score(trace):
    return openai.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": template_tone_eval.format(text=trace.output),
            }
        ],
        model="gpt-4o",
        temperature=0
    ).choices[0].message.content
    # print(f"User query: {traces_batch[1].input['args'][0]}")
    # print(f"Model answer: {traces_batch[1].output}")
    # print(f"Dominant tones: {test_tone_score}")    
    
for page_number in range(1, math.ceil(TOTAL_TRACES/BATCH_SIZE)):
 
    traces_batch = langfuse.fetch_traces(
        page=page_number,
        from_timestamp=five_am_yesterday,
        to_timestamp=five_am_today,
        limit=BATCH_SIZE
    ).data
 
    for trace in traces_batch:
        print(f"Processing {trace.name}")
 
        if trace.output is None:
            print(f"Warning: \n Trace {trace.name} had no generated output, \
            it was skipped")
            continue
        
        # tone_score(trace) calcualte via another LLM or external service    
        langfuse.score(
            trace_id=trace.id,
            name="tone",
            value="positive negative neutral",
        )
 
        jscore = 1 # calcualte via another LLM or external service
        langfuse.score(
            trace_id=trace.id,
            name="joyfulness",
            value=1,
            comment="testing"
        )
 
    print(f"Batch {page_number} processed 🚀 \n")