from typing import Dict, Any
from ..pipeline.chat_pipeline import ChatPipeline

def run_chat_cli(config: Dict[str, Any]) -> None:
    """
    Run the chat CLI with the given configuration
    """
    # Initialize the pipeline
    pipeline = ChatPipeline(config)

    # Enhanced welcome message
    print("\n" + "="*50)
    print(f"Welcome to {config['name']} (v{config['version']})")
    print(f"{config['description']}")
    print("\nTechnical Details:")
    print(f"- Model: {config['components']['model']}")
    print(f"- Temperature: {config['parameters']['temperature']}")
    print("\nType 'quit' or 'exit' to end the session")
    print("="*50 + "\n")

    while True:
        user_input = input("You: ").strip()

        if user_input.lower() in ['quit', 'exit']:
            print("\nEnding chat session...")
            break
        
        try:
            # Get response from pipeline
            assistant_message = pipeline.get_response(user_input)
            print(f"\nAssistant: {assistant_message}\n")
        
        except Exception as e:
            print(f"\nError: {str(e)}\n")
            continue