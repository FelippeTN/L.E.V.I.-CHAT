import json, os
import logging
import base64
import requests
from groq import Groq
from dotenv import load_dotenv
from utils.chat_services import PromptProcessor, PDFProcessor 


logging.basicConfig(filename='debug_log.txt', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


load_dotenv()


class GroqChat:
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API"))
        self.prompt_processor = PromptProcessor()
        self.pdf_processor = PDFProcessor()
        logging.debug("GroqChatbot inicializado com sucesso.")

    def send_prompt(self, prompt: str, pdf_base64_or_path: str = None):
        logging.debug(f"Prompt recebido: {prompt}")
        pdf_base64 = None

        if pdf_base64_or_path:
            try:
                base64.b64decode(pdf_base64_or_path, validate=True)
                pdf_base64 = pdf_base64_or_path
            except Exception:
                pdf_base64 = self.pdf_processor.pdf_to_base64(pdf_base64_or_path)

        processed_prompt = self.prompt_processor.process_prompt(prompt, pdf_base64)
        logging.debug(f"Prompt processado: {processed_prompt}")

        try:
            chat_completion = self.client.chat.completions.create(
                messages=[{"role": "user", "content": processed_prompt}],
                model="llama3-8b-8192"
            )
            response_content = chat_completion.choices[0].message.content
            logging.debug(f"Resposta recebida da Groq API: {response_content}")

            return {
                "prompt": prompt,
                "processed_prompt": processed_prompt,
                "response": response_content
            }

        except Exception as e:
            logging.error(f"Erro ao chamar a Groq API: {str(e)}")
            raise e


class LlamaChat:
    def __init__(self):
        self.url_llama_cpp = 'http://localhost:8000/v1/chat/completions'
        self.prompt_processor = PromptProcessor()
        self.pdf_processor = PDFProcessor()
        logging.debug("LlamaChat inicializado com sucesso.")

    def send_prompt(self, prompt: str, pdf_base64_or_path: str = None):
        logging.debug(f"Prompt recebido: {prompt}")
        pdf_base64 = None

        if pdf_base64_or_path:
            try:
                base64.b64decode(pdf_base64_or_path, validate=True)
                pdf_base64 = pdf_base64_or_path
            except Exception:
                pdf_base64 = self.pdf_processor.pdf_to_base64(pdf_base64_or_path)

        processed_prompt = self.prompt_processor.process_prompt(prompt, pdf_base64)
        logging.debug(f"Prompt processado: {processed_prompt}")

        data = {
            "messages": [{"role": "user", "content": processed_prompt}],
            "model": "llama3-8b-8192"
        }

        try:
            response = requests.post(self.url_llama_cpp, headers={"Content-Type": "application/json"}, data=json.dumps(data))

            if response.status_code == 200:
                response_json = response.json()
                logging.debug(f"Resposta recebida da LLM API: {response_json}")

                return {
                    "prompt": prompt,
                    "processed_prompt": processed_prompt,
                    "response": response_json.get("choices", [{}])[0].get("message", {}).get("content", "")
                }

            else:
                logging.error(f"Erro ao chamar a LLM API: Status Code {response.status_code}, Resposta: {response.text}")
                raise Exception(f"Erro ao chamar a LLM API: {response.text}")

        except Exception as e:
            logging.error(f"Erro ao chamar a LLM API: {str(e)}")
            raise e
