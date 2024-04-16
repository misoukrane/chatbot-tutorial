# use gradio to create a chatbot that uses qadrant to search for similar text

import json
import gradio as gr
from openai import OpenAI
from qdrant_client import QdrantClient

# constants
COLLECTION_NAME = "codereliant"
EMBEDDING_MODEL = "text-embedding-3-small"

# clients
openai_client = OpenAI()
client = QdrantClient(url="http://localhost:6333")

def search_similar_text(text):
    hits = client.search(
        collection_name=COLLECTION_NAME,
        query_vector=openai_client.embeddings.create(input=[text],model=EMBEDDING_MODEL,)
        .data[0]
        .embedding,
        limit=3,
    )
    return hits

def generate_response(query, history):
    hits = search_similar_text(query)
    # create the context based on the hits
    context = ""
    for hit in hits:
        context += json.dumps(hit.payload) + "\n"
    prompt = generate_prompt(context, query)
    completion = openai_client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": "You are codereliant chatbot, skilled in answering questions about codereliant.io."},
            {"role": "user", "content": prompt}
        ]
    )
    
    return completion.choices[0].message.content

def generate_prompt(context, query):
    prompt = f"""
Context:
{context}

Query: {query}

Based on the provided context, answer the query. If the context does not contain enough information to answer the query, respond with "I'm sorry, but the provided context does not have sufficient information to answer your query. Also, answer like a customer service representative would."

Answer:
"""
    return prompt

demo = gr.ChatInterface(fn=generate_response, examples=[ "what is this website about?","what can I learn from codereliant?", "Do you have any SRE interview preparation posts?"], title="CodeReliant Bot", multimodal=False)
demo.launch()

