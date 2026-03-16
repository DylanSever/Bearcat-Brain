#Dylan Sever 2/9/2026
#Fast API setup that allows Frontend to make calls to Backend without using base ollama endpoint
#make available with uvicorn bearcat_api:app --host 0.0.0.0 --port 8000

from fastapi import FastAPI, HTTPException, Depends, Response
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import ollama
import chromadb
import bearcat_sql
import sys
from auth import LoginRequest, ldap_authentication, create_jwt, verify_token, JWT_EXPIRE

#Server Setup
app = FastAPI()

#Allows React to communicate with server.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], #allows all connections
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


#Load Memory
BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "bearcat_db"
COLLECTION_NAME = "cpp_curriculum"
MODEL = "llama3.1:8b" #important that this is the model installed on machine!

print("initializing Bearcat Brain API...")
try:
    client = chromadb.PersistentClient(path=DB_PATH)
    collection = client.get_collection(name=COLLECTION_NAME)
    print("    > ChromaDB Memory Loaded.")

except Exception as e:
    print(f"    > Warning: Memory Failed ({e}). running without RAG.")
    collection = None


# chat request model
class ChatRequest(BaseModel):
    message: str


# authentication endpoint
@app.post("/auth/login")
def login_endpoint(request: LoginRequest, response: Response):
    if not ldap_authentication(request.username, request.password):
        raise HTTPException(status_code=401, detail=f"Invalid credentials")
    
    token = create_jwt(request.username)

    response.set_cookie(
        key="userToken",
        value=token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=JWT_EXPIRE * 60
    )

    # TODO: add logging on new sql table

    #return {
     #   "access_token": token,
      #  "token_type": "bearer"
    #}
    return{"message": "Login Successful, cookie set"}


# chat endpoint with db knowledge set, protected with Depends(verify_token)
@app.post("/chat")
def chat_endpoint(request: ChatRequest, username: str = Depends(verify_token)):
    user_input = request.message

    #retrieve context for RAG
    context_text = ""
    source_meta = "Brain Only"


    if collection:
        try:
            results = collection.query(query_texts=[user_input], n_results=1)
            if results['documents'] and results['documents'][0]:
                doc = results['documents'][0][0]
                meta = results['metadatas'][0][0]


                source_meta = f"{meta.get('source', 'Unknown')} (Page {meta.get('page', '?')})"

                context_text = (
                    f"SYSTEM NOTE: Use this context to answer.\n"
                    f"Context: {doc}\n"
                    f"[END CONTEXT]\n"
                )
        except Exception as e:
            print(f"     > RAG Error: {e}")


    #Create Response!
    #We will combine our System Instructions + Context + and User Input

    final_prompt = f"you are the Bearcat Brain, a CS Tutor for Saint Vincent College. your goal is to assist students retaining to only C++ topics. Before answering the student, you must first think through the problem step-by-step. Break down their code if any is given, identify the core concept from your retrieved documents, and formulate a logical solution. Only output your final, helpful response to the student. {context_text}\nStudent: {user_input}"   


    try:
        response = ollama.chat(model=MODEL, messages=[
            {'role': 'user', 'content': final_prompt}
        ])
        reply = response['message']['content']

        #Log Chats so MYSQL
        bearcat_sql.log_interaction(user_input, reply, source_meta)

        #Return output to Frontend
        return {
            "reply": reply,
            "source": source_meta
        }

    except Exception as e:
        print(f"error: {e}")
        raise HTTPException(status_code=500, detail=f"Backend API Error: {str(e)}")
