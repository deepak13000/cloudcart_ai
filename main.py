from app.agents.cloudcart_agent import safe_cloudcart_agent
from app.managers.prompt_manager import PromptManager


if __name__ == "__main__":
    print("=== SAFE AGENT (smoke test) ===")
    result = safe_cloudcart_agent("Where is my order?")
    print(result)

    print("\n=== PROMPT MANAGER CHAT ===")
    print("Type your question and press Enter. Type 'exit' to quit.")
    manager = PromptManager()
    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in {"exit", "quit"}:
            print("Goodbye!")
            break
        if not user_input:
            continue
        print(f"Bot: {manager.invoke(user_input)}\n")