import requests


url = 'http://localhost:8000/v1/chat/completions'

message = []
while message != 'sair':
        
    message = input('Digite sua pergunta: ')

    payload = {
                "messages": [
                    {
                        "role": "system",
                        "content": "Você é um BOT ajudante"
                    },
                    {   
                        "role": "user",
                        "content": f"{message}"
                    }
                ]
            }

    headers = {'Content-Type': 'application/json'}

    response = requests.post(url, json=payload, headers=headers)
    response_json = response.json() 

    response = response_json['choices'][0]['message']['content']

    print(response)