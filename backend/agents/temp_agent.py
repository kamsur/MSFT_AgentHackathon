import os
from openai import AzureOpenAI
from datetime import datetime

def initialize_client():
    """Initialize the Azure OpenAI client"""
    endpoint = os.getenv("PROJECT_ENDPOINT", "https://hackathon-group6-123.services.ai.azure.com")
    deployment = os.getenv("MODEL_DEPLOYMENT_NAME", "gpt-4.1")
    subscription_key = os.getenv("SUBSCRIPTION_KEY", "ApkSH2yYEJr03QypDtkp7K6ub2Zd4FCEntVvUCPs68uzmDvyYpYdJQQJ99BGACYeBjFXJ3w3AAAAACOGauXV")
    api_version = os.getenv("API_VERSION", "2024-12-01-preview")

    return AzureOpenAI(
        api_version=api_version,
        azure_endpoint=endpoint,
        api_key=subscription_key,
    ), deployment

def save_conversation(messages, filename="conversation_history.txt"):
    """Save the conversation history to a file"""
    try:
        os.makedirs("backend/agents/output", exist_ok=True)
        filepath = f"backend/agents/output/{filename}"
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"Conversation History - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 50 + "\n\n")
            for message in messages:
                role = message["role"].upper()
                content = message["content"]
                f.write(f"{role}: {content}\n\n")
        print(f"Conversation saved to {filepath}")
    except Exception as e:
        print(f"Error saving conversation: {e}")

def main():
    """Main conversation loop"""
    print("Welcome to the AI Chat Assistant!")
    print("Type 'quit', 'exit', or 'bye' to end the conversation.")
    print("Type 'save' to save the conversation history.")
    print("-" * 50)

    # Initialize client and conversation
    client, deployment = initialize_client()
    
    # Initialize conversation with system message
    messages = [
        {
            "role": "system",
            "content": "You are a helpful assistant. Be conversational and engaging while providing accurate and useful information."
        }
    ]

    while True:
        # Get user input
        try:
            user_input = input("\nYou: ").strip()
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break

        # Check for exit commands
        if user_input.lower() in ['quit', 'exit', 'bye']:
            print("Goodbye!")
            break
        
        # Check for save command
        if user_input.lower() == 'save':
            save_conversation(messages)
            continue

        # Skip empty inputs
        if not user_input:
            continue

        # Add user message to conversation
        messages.append({
            "role": "user",
            "content": user_input
        })

        try:
            # Get response from Azure OpenAI
            print("Assistant: ", end="", flush=True)
            
            response = client.chat.completions.create(
                messages=messages,
                max_completion_tokens=4000,
                temperature=0.7,
                top_p=1.0,
                frequency_penalty=0.0,
                presence_penalty=0.0,
                model=deployment,
                stream=True  # Enable streaming for better user experience
            )

            # Collect and display the streaming response
            assistant_response = ""
            for chunk in response:
                if chunk.choices and len(chunk.choices) > 0 and chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    print(content, end="", flush=True)
                    assistant_response += content
            
            print()  # New line after response

            # Add assistant response to conversation
            if assistant_response:
                messages.append({
                    "role": "assistant",
                    "content": assistant_response
                })

        except Exception as e:
            print(f"Error getting response: {e}")
            print("Please try again.")

    # Auto-save conversation on exit
    if len(messages) > 1:  # Only save if there was actual conversation
        save_conversation(messages, f"conversation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")

if __name__ == "__main__":
    main()