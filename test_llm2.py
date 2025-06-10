from langchain_community.llms import Ollama

llm = Ollama(model="mistral:7b-instruct")
response = llm.invoke("Quelle est la capitale de la France?")
print(response)
