from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import List
import google.generativeai as genai
from pinecone import Pinecone
from app.core.config import PINECONE_API_KEY, GEMINI_API_KEY, INDEX_NAME  # Assuming a default index name is defined

router = APIRouter()

# Initialize Google Gemini API
genai.configure(api_key=GEMINI_API_KEY)

# Initialize Pinecone
pc = Pinecone(api_key=PINECONE_API_KEY)

class QueryRequest(BaseModel):
    query: str  # Only query is required now

# Function to query Gemini for embeddings
def query_gemini(query: str) -> List[float]:
    try:
        result = genai.embed_content(model="models/text-embedding-004", content=[query])
        if 'embedding' not in result or not result['embedding']:
            raise HTTPException(status_code=500, detail="Failed to generate embedding for the query.")
        return result['embedding'][0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error querying Gemini: {str(e)}")

# Function to query Pinecone
def query_pinecone(index_name: str, query_vector: List[float], top_k: int = 5):
    index = pc.Index(index_name)
    try:
        return index.query(vector=query_vector, top_k=top_k, include_metadata=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error querying Pinecone: {str(e)}")

# Function to generate response using Gemini
def generate_response(question: str, context: str) -> str:
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
    prompt = (
        f"Question: {question}\n"
        f"Context: {context}\n"
        "Instructions: Based on the provided context, generate a concise and natural-sounding answer to the question. "
        "If the context doesn't contain relevant information, politely state that you don't have enough information to answer accurately. "
        "Respond in a conversational tone as if you're chatting with the user.\n"
        "Answer:"
    )
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating response: {str(e)}")

# API Route for handling queries
@router.api_route("/query/", methods=["GET", "POST"])
async def perform_query(request: Request):
    print("Received request", request.body)

    # Default index name
    index_name = INDEX_NAME  # Use default index if no index_name is provided

    if request.method == "GET":
        query = request.query_params.get("query")
    elif request.method == "POST":
        body = await request.json()
        query = body.get("query")
    else:
        raise HTTPException(status_code=405, detail="Method not allowed")

    # Validate input
    if not query:
        raise HTTPException(status_code=400, detail="Missing query parameter")

    # Generate embedding for the query
    query_embedding = query_gemini(query)
    if not query_embedding:
        raise HTTPException(status_code=400, detail="Failed to process the query.")

    # Query Pinecone
    results = query_pinecone(index_name, query_embedding)
    if not results or not results.get('matches'):
        return {"response": "I couldn't find any relevant information to answer your question. Is there something else I can help you with?"}

    # Process results
    contexts = []
    for match in results['matches']:
        question = match.get('metadata', {}).get('question', '')
        answer = match.get('metadata', {}).get('answer', '')
        contexts.append(f"Q: {question}\nA: {answer}")

    combined_context = "\n\n".join(contexts)
    
    # Generate response
    response = generate_response(query, combined_context)
    return {"response":response}