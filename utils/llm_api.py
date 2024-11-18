import json
import logging
import base64
import requests
from groq import Groq
from utils.chat_services import PromptProcessor, PDFProcessor 

logging.basicConfig(filename='debug_log.txt', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class GroqChat:
    def __init__(self, api_key: str):
        self.client = Groq(api_key=api_key)
        self.prompt_processor = PromptProcessor()
        self.pdf_processor = PDFProcessor()
        logging.debug("////////////////////////////// INIT //////////////////////////////////////////////")
        logging.debug("GroqChatbot inicializado com sucesso.")

    def send_prompt(self, prompt: str, pdf_base64_or_path: str = None):
        # Log do prompt inicial
        logging.debug(f"Prompt recebido: {prompt}")

        # Variável para armazenar o PDF em base64
        pdf_base64 = None
        
        # Verificar e converter PDF para base64, se necessário
        if pdf_base64_or_path:
            try:
                # Tenta decodificar o base64 para verificar se já está no formato correto
                base64.b64decode(pdf_base64_or_path, validate=True)
                logging.debug("O PDF estava em base64.")
                pdf_base64 = pdf_base64_or_path
            except Exception:
                # Se a decodificação falhar, considera que é um caminho de arquivo e converte
                logging.debug("O PDF não estava em base64. Convertendo para base64.")
                pdf_base64 = self.pdf_processor.pdf_to_base64(pdf_base64_or_path)
                logging.debug(f"base64 Code: {pdf_base64}")

        # Processa o prompt, incluindo o PDF se fornecido
        processed_prompt = self.prompt_processor.process_prompt(prompt, pdf_base64)
        logging.debug(f"Prompt processado: {processed_prompt}")

        # Envia o prompt processado para a API Groq
        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": processed_prompt,
                    }
                ],
                model="llama3-8b-8192"  # Modelo pode ser ajustado se necessário
            )
            response_content = chat_completion.choices[0].message.content
            logging.debug(f"Resposta recebida da Groq API: {response_content}")

            # Preparando o retorno como JSON de maneira mais legível
            response_json = {
                "prompt": prompt,
                "processed_prompt": processed_prompt,
                "response": response_content
            }
            
            logging.debug("////////////////////////////// END //////////////////////////////////////////////")
            
            # Retornando o JSON formatado sem escapes desnecessários
            return json.loads(json.dumps(response_json, ensure_ascii=False, indent=4))

        except Exception as e:
            logging.error(f"Erro ao chamar a Groq API: {str(e)}")
            raise e

logging.basicConfig(filename='debug_log.txt', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
class LlamaChat:
    def __init__(self, url_llama_cpp: str):
        self.url_llama_cpp = 'http://localhost:8000/v1/chat/completions'
        self.prompt_processor = PromptProcessor()
        self.pdf_processor = PDFProcessor()
        logging.debug("////////////////////////////// INIT //////////////////////////////////////////////")
        logging.debug("LlamaChat inicializado com sucesso.")

    def send_prompt(self, prompt: str, pdf_base64_or_path: str = None):
        # Log do prompt inicial
        logging.debug(f"Prompt recebido: {prompt}")

        # Variável para armazenar o PDF em base64
        pdf_base64 = None
        
        # Verificar e converter PDF para base64, se necessário
        if pdf_base64_or_path:
            try:
                # Tenta decodificar o base64 para verificar se já está no formato correto
                base64.b64decode(pdf_base64_or_path, validate=True)
                logging.debug("O PDF estava em base64.")
                pdf_base64 = pdf_base64_or_path
            except Exception:
                # Se a decodificação falhar, considera que é um caminho de arquivo e converte
                logging.debug("O PDF não estava em base64. Convertendo para base64.")
                pdf_base64 = self.pdf_processor.pdf_to_base64(pdf_base64_or_path)
                logging.debug(f"base64 Code: {pdf_base64}")

        # Processa o prompt, incluindo o PDF se fornecido
        processed_prompt = self.prompt_processor.process_prompt(prompt, pdf_base64)
        logging.debug(f"Prompt processado: {processed_prompt}")

        # Configura os dados para enviar ao LLM
        data = {
            "messages": [
                {
                    "role": "user",
                    "content": processed_prompt,
                }
            ]
        }

        # Envia o prompt processado para o endpoint via POST request
        try:
            response = requests.post(self.url_llama_cpp, headers={"Content-Type": "application/json"}, data=json.dumps(data))

            # Verifica se o pedido foi bem-sucedido
            if response.status_code == 200:
                response_json = response.json()
                logging.debug(f"Resposta recebida da LLM API: {response_json}")

                # Preparando o retorno como JSON de maneira mais legível
                final_response = {
                    "prompt": prompt,
                    "processed_prompt": processed_prompt,
                    "response": response_json.get("choices", [{}])[0].get("message", {}).get("content", "")
                }
                
                logging.debug("////////////////////////////// END //////////////////////////////////////////////")
                
                # Retornando o JSON formatado sem escapes desnecessários
                return json.loads(json.dumps(final_response, ensure_ascii=False, indent=4))

            else:
                logging.error(f"Erro ao chamar a LLM API: Status Code {response.status_code}, Resposta: {response.text}")
                raise Exception(f"Erro ao chamar a LLM API: {response.text}")

        except Exception as e:
            logging.error(f"Erro ao chamar a LLM API: {str(e)}")
            raise e