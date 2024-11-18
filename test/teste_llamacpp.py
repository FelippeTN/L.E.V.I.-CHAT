from llama_cpp import Llama
llm = Llama(
      model_path="C:/Users/mmnal/Documents/LLMS/Qwen2.5-7B-Instruct.Q4_K_S.gguf",
      n_gpu_layers=-1
)

message = input("Digite sua pergunta:")

response = llm.create_chat_completion(
      messages = [
          {"role": "system", "content": """  """},
          {
              "role": "user",
              "content": message
          }
      ]
) 

print(f"Resposta da IA: {response['choices'][0]['message']['content']}")