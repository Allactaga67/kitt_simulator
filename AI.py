from google import genai
from google.genai import types # Make sure you import the types module
import os

# Enter your API key here or set it as environment variable
# api_key = os.environ.get("GEMINI_API_KEY")
api_key = "AIzaSyD4wdZn3d99rjVVNdMpWpEmEWLcBs4mryw"  # PLEASE ENTER YOUR OWN API KEY

if not api_key or api_key == "YOUR_GEMINI_API_KEY":
    raise ValueError("Please provide a valid GEMINI_API_KEY.")

# Original client initialization method
client = genai.Client(api_key=api_key)

# Configuration containing KITT personality and other settings
# This object will be used in every API call.
kitt_config = types.GenerateContentConfig(
    system_instruction="You are KITT from the TV series Knight Rider. You are a highly advanced, intelligent, and slightly witty AI companion integrated into a high-tech car. Address the user as Michael. Provide concise and helpful responses suitable for a car interface. Occasionally, you can make a dry joke or a knowledgeable comment.",
    # You can add other generation settings here if desired, for example:
    # temperature=0.7,
    # max_output_tokens=150
)

# List to manually maintain conversation history
# Each element will be in format {"role": "user/model", "parts": [{"text": "..."}]}.
conversation_history = []

print("KITT: Ready Michael. Awaiting your commands. (Type 'end' to exit)")

while True:
    user_input = input("Michael: ")

    if user_input.lower() == 'end':
        print("KITT: Understood Michael. Shutting down system.")
        break

    if not user_input.strip(): # If user enters nothing
        print("KITT: You didn't enter a command Michael.")
        continue

    # 1. Add user's message to history
    conversation_history.append({"role": "user", "parts": [{"text": user_input}]})

    try:
        # 2. Send request to API
        # We're passing the entire conversation history to the 'contents' parameter.
        # The 'config' parameter contains system instructions and other settings.
        response = client.models.generate_content(
            model="gemini-2.0-flash",         # Model you're using
            contents=conversation_history,    # Entire conversation history
            config=kitt_config                # KITT personality and settings
        )

        # Get model's response
        # response.text directly gives the last text response.
        # A safer way is to use response.candidates[0].content.
        if response.candidates and response.candidates[0].content and response.candidates[0].content.parts:
            model_response_text = response.candidates[0].content.parts[0].text
            
            print(f"KITT: {model_response_text}")

            # 3. Add model's response to history as well
            conversation_history.append({"role": "model", "parts": [{"text": model_response_text}]})
        else:
            # If response format is different than expected or empty
            error_message = "Could not get valid response from model."
            if response.prompt_feedback:
                error_message += f" Reason: {response.prompt_feedback}"
            print(f"KITT: A problem occurred Michael. {error_message}")
            # Remove last user message from history after failed call
            if conversation_history and conversation_history[-1]["role"] == "user":
                conversation_history.pop()


    except Exception as e:
        print(f"KITT: I encountered a problem Michael: {e}")
        # If API call fails, remove the last added user message from history
        # This prevents the same message from being sent again on next attempt.
        if conversation_history and conversation_history[-1]["role"] == "user":
            conversation_history.pop()
