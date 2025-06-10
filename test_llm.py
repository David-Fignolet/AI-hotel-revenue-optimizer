from src.llm.llm_manager import LLMManager

def main():
    print("Test du gestionnaire LLM...")
    llm = LLMManager()
    
    prompt = "Quelles sont les meilleures pratiques pour fixer les prix des chambres d'hôtel ?"
    print(f"\nPrompt: {prompt}")
    
    response = llm.generate_response(prompt)
    print(f"\nRÉPONSE:\n{response}")

if __name__ == "__main__":
    main()
