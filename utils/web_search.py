from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from groq import Groq
import requests
import json
import textwrap

client = Groq()
url_llama = 'http://localhost:8000/v1/chat/completions'

def gerar_termos_busca(prompt_usuario: str) -> str:
    prompt_llm = ( 
        f"Transforme o seguinte pedido do usuário em termos otimizados para uma busca em mecanismos de busca: '{prompt_usuario}' "
        f"Responda com uma linha contendo apenas os termos mais relevantes (termos_relevantes)."
    )
    
    try:
        payload = {
                "messages": [
                    { 
                        "role": "system",
                        "content": "Você é um assistente que responde sempre em JSON.",
                    },
                    { 
                        "role": "user",
                        "content": prompt_llm
                    }
                ]
            }
     

        headers = {'Content-Type': 'application/json'}

        response = requests.post(url_llama, json=payload, headers=headers)
        response_json = response.json() 
    
        # A resposta deve ser analisada como JSON
        response_json = json.loads(response_json['choices'][0]['message']['content'])    
        
        # Corrigido: converter lista para string, caso "termos_relevantes" seja uma lista
        termos_relevantes = response_json.get("termos_relevantes", "")
        
        # Verificar se é uma lista e converter para string
        if isinstance(termos_relevantes, list):
            return " ".join(termos_relevantes)
        
        return termos_relevantes
    
    except Exception as e:
        print(f"Erro ao gerar termos de busca: {e}")
        return ""

async def extrair_dados_bing(termos_busca: str):
    resultados_extracao = []
    lista_url = []

    try:
        # Playwright precisa ser chamado de forma assíncrona
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            # Garantir que "termos_busca" seja uma string antes de formatar a URL
            termos_busca_str = termos_busca.replace(" ", "+")
            url = f'https://www.bing.com/search?q={termos_busca_str}'
            await page.goto(url)
            await page.wait_for_selector('li.b_algo')

            resultados = await page.query_selector_all('li.b_algo')

            for resultado in resultados:
                titulo = await resultado.query_selector('h2')
                titulo_texto = await titulo.inner_text() if titulo else 'Sem título'
                link = await resultado.query_selector('a')
                link_url = await link.get_attribute('href') if link else 'Sem link'
                resultados_extracao.append({'titulo': titulo_texto, 'link': link_url})
                lista_url.append(link_url)
            
                
            await browser.close()
    except Exception as e:
        print(f"Erro ao extrair dados do Bing: {e}")

    return resultados_extracao, lista_url[:2]

def bing_search(resultados_extracao, prompt_user: str):
    """
    Função para extrair informação dos links criados em 'extrair_dados_bing()'.
    """
    
    informacao_extraida = []
    count_links = 0
    max_length = 5000


    for resultado in resultados_extracao:
        if count_links <=2:
            link = resultado.get('link') 
            
            if not link:
                continue  
            
            print(f"Acessando o link: {link}")
            try:

                response = requests.get(link)
                
                if response.status_code == 200:
                    
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    texto = soup.get_text(separator=' ', strip=True)

                    texto_limitado = textwrap.shorten(texto, width=max_length, placeholder="...")
                    
                    informacao_extraida.append(texto_limitado)

                    count_links+=1
                else:
                    print(f"Falha ao acessar a página: {response.status_code}")
        
            except Exception as e:
                print(f"Erro ao acessar o link: {e}")

            


    payload = {
                "messages": [
                    { 
                        "role": "system",
                        "content": "Você é um BOT assistente",
                    },
                    { 
                        "role": "user",
                        "content": f"""Responda assim: 'De acordo com a extração da Web:', e explique o texto de acordo com a pergunta do usuario.
                        pergunta do usuario:{prompt_user}.
                        texto extraido da web: {informacao_extraida}"""
                    }
                ]
            }
  
    
    headers = {'Content-Type': 'application/json'}

    response = requests.post(url_llama, json=payload, headers=headers)
    response_json = response.json() 
    print(response_json)

    
    response_json = {
                "prompt": prompt_user,
                "processed_prompt": response_json['choices'][0]['message']['content'],
                "response": response_json['choices'][0]['message']['content']
            }
    
    respose_json_formatted = json.loads(json.dumps(response_json, ensure_ascii=False, indent=4))
    print(f'response: {respose_json_formatted}')
    
    return respose_json_formatted
        

