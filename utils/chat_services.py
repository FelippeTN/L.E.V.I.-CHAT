import base64
import io
from PyPDF2 import PdfReader
import fitz  # PyMuPDF
from PIL import Image
import pytesseract
from langchain.schema import Document
import re
import http.client
from urllib.parse import urlparse

class PDFProcessor:
    def __init__(self, words_per_line=10):
        self.words_per_line = words_per_line

    def extract_document(self, pdf_base64: str) -> list:
        pdf_binary = base64.b64decode(pdf_base64)
        try:
            pdf_reader = PdfReader(io.BytesIO(pdf_binary))
            pdf_file = fitz.open(stream=io.BytesIO(pdf_binary))
        except Exception as e:
            raise Exception(f"Erro ao abrir o PDF: {e}")

        total_pages = len(pdf_reader.pages)
        texto_inicial = ""

        for page_num in range(total_pages):
            page = pdf_reader.pages[page_num]
            text = page.extract_text()
            if not text:
                page = pdf_file.load_page(page_num)
                pix = page.get_pixmap()
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                width, height = img.size
                top_margin = int(height * 0.1)
                bottom_margin = int(height * 0.1)
                roi = img.crop((0, top_margin, width, height - bottom_margin))
                text = pytesseract.image_to_string(roi)
            texto_inicial += text + "\n"

        # Quebra as linhas a cada 'words_per_line' palavras
        words = texto_inicial.split()
        formatted_text = ""
        for i in range(0, len(words), self.words_per_line):
            formatted_text += ' '.join(words[i:i + self.words_per_line]) + '\n'

        langchain_document = [
            Document(page_content=formatted_text.strip(), metadata={"source": "base64_input"})
        ]
        return langchain_document

    # Lê o arquivo PDF e codifica em base64
    def pdf_to_base64(self, file_path: str) -> str:
        with open(file_path, "rb") as pdf_file:
            pdf_binary = pdf_file.read()
            return base64.b64encode(pdf_binary).decode('utf-8')


#inicializar a classe de processar prompt
class PromptProcessor:
    def __init__(self):
        self.pdf_processor = PDFProcessor()

    def process_prompt(self, prompt: str, pdf_base64: str = None) -> str:
        # Checa se um PDF base64 foi fornecido
        if pdf_base64:
            document = self.pdf_processor.extract_document(pdf_base64)
            extracted_text = "\n".join([doc.page_content for doc in document])
            prompt += f"\n\n{extracted_text}"  # Adiciona o texto do PDF abaixo do prompt, com uma linha de separação

        # Retorna a string formatada
        return prompt
