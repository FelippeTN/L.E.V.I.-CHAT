from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import base64
from utils.llm_api import GroqChat, LlamaChat
from fastapi.middleware.cors import CORSMiddleware
from utils.web_search import gerar_termos_busca, extrair_dados_bing, bing_search
import asyncio

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


groq_chatbot = GroqChat()
llama3_sync = LlamaChat()

class PromptRequest(BaseModel):
    prompt: str
    pdf_base64: Optional[str] = None
    pdf_path: Optional[str] = None
    web_search: Optional[bool] = False

async def handle_web_search(prompt: str):
    termo_busca = gerar_termos_busca(prompt)
    search, link_url = await extrair_dados_bing(termo_busca)
    web_response = bing_search(search, prompt)
    return web_response, link_url

def handle_pdf_input(pdf_base64: Optional[str], pdf_path: Optional[str]):
    if pdf_base64:
        try:
            base64.b64decode(pdf_base64, validate=True)
            return pdf_base64
        except Exception:
            raise HTTPException(status_code=400, detail="PDF em base64 inválido.")
    elif pdf_path:
        try:
            with open(pdf_path, "rb") as pdf_file:
                return base64.b64encode(pdf_file.read()).decode('utf-8')
        except Exception:
            raise HTTPException(status_code=500, detail="Erro ao ler o arquivo PDF.")
    return None

async def process_request(request: PromptRequest, chatbot):
    pdf_base64_or_path = handle_pdf_input(request.pdf_base64, request.pdf_path)
    
    if request.web_search:
        web_response, links = await handle_web_search(request.prompt)
    else:
        web_response, links = None, None
    

    try:
        response = chatbot.send_prompt(request.prompt, pdf_base64_or_path=pdf_base64_or_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar o prompt: {str(e)}")

    return {
        "prompt": request.prompt,
        "response": web_response or response,
        "links": links
    }

@app.post("/groq_chat")
async def process_prompt(request: PromptRequest):
    return await process_request(request, groq_chatbot)

@app.post("/llama_chat")
async def llm_chat_endpoint(request: PromptRequest):
    return await process_request(request, llama3_sync)
