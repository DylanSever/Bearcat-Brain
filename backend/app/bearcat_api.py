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
    allow_origins=[
	# 1. Local React Testing
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        
        # 2. Production Domain
        "https://cis2.stvincent.edu",  
        
        # 3. Nginx / Frontend IP
        "http://10.25.1.251",
        
        # 4. Backend Server IP (Just to be perfectly safe!)
        "http://10.25.1.49",
        "http://10.25.1.49:8000"], #allegedly * doesnt work with cookies!
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
        print(" LDAP FAILED")
        raise HTTPException(status_code=401, detail=f"Invalid credentials")
    print("JWT created")
    token = create_jwt(request.username)

    # TODO: add logging on new sql table

    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=True,
        samesite="strict",
        max_age=60 * 480
    )

    return { "message": "Login successful" }


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
