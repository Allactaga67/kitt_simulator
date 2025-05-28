from google import genai
from google.genai import types # Make sure to import the types module
import os
from gtts import gTTS
import argparse
import pygame
import time

# Enter your API key here or set it as an environment variable
# api_key = os.environ.get("GEMINI_API_KEY")
api_key = "AIzaSyD4wdZn3d99rjVVNdMpWpEmEWLcBs4mryw"  # PLEASE ENTER YOUR OWN API KEY

if not api_key or api_key == "YOUR_GEMINI_API_KEY":
    raise ValueError("Please provide a valid GEMINI_API_KEY.")

# Initialize client as in your original setup
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
# Each element will be in the format {"role": "user/model", "parts": [{"text": "..."}]}
conversation_history = []

print("KITT: Ready Michael. Awaiting your commands. (Type 'end' to exit)")

class AI:
    def __init__(self, use_voice=True):
        self.use_voice = use_voice
        pygame.mixer.init()
        
    def speak(self, text):
        """Convert text to speech and play it"""
        if not self.use_voice:
            return
            
        try:
            # Create gTTS object
            tts = gTTS(text=text, lang='en', slow=False)
            
            # Save the audio file
            temp_file = "temp_speech.mp3"
            tts.save(temp_file)
            
            # Play the audio
            pygame.mixer.music.load(temp_file)
            pygame.mixer.music.play()
            
            # Wait for the audio to finish playing
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
                
            # Clean up
            pygame.mixer.music.unload()
            os.remove(temp_file)
            
        except Exception as e:
            print(f"Error in speech: {str(e)}")

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--voice', action='store_true', help='Enable voice output')
    parser.add_argument('--no-voice', action='store_true', help='Disable voice output')
    args = parser.parse_args()
    
    # Determine voice setting
    use_voice = True
    if args.no_voice:
        use_voice = False
    
    # Initialize AI
    ai = AI(use_voice=use_voice)
    
    print("AI Mode Started")
    if use_voice:
        ai.speak("AI Mode Started")
    
    try:
        while True:
            user_input = input("Michael: ")
            if user_input.lower() in ['exit', 'quit', 'bye', 'end']:
                print("KITT: Goodbye Michael!")
                if use_voice:
                    ai.speak("Goodbye Michael!")
                break
                
            if not user_input.strip(): # If user enters nothing
                print("KITT: You didn't enter a command, Michael.")
                if use_voice:
                    ai.speak("You didn't enter a command, Michael.")
                continue

            # 1. Add user's message to history
            conversation_history.append({"role": "user", "parts": [{"text": user_input}]})

            try:
                # 2. Send request to API
                # We're passing the entire conversation history to the 'contents' parameter.
                # The 'config' parameter contains system instructions and other settings.
                response = client.models.generate_content(
                    model="gemini-2.0-flash",         # The model you're using
                    contents=conversation_history,    # Entire conversation history
                    config=kitt_config                # KITT personality and settings
                )

                # Get the model's response
                # response.text directly gives the last text response.
                # A safer approach is to use response.candidates[0].content.
                if response.candidates and response.candidates[0].content and response.candidates[0].content.parts:
                    model_response_text = response.candidates[0].content.parts[0].text
                    
                    print(f"KITT: {model_response_text}")

                    # 3. Add model's response to history as well
                    conversation_history.append({"role": "model", "parts": [{"text": model_response_text}]})
                    
                    if use_voice:
                        ai.speak(model_response_text)
                else:
                    # If response format is different than expected or empty
                    error_message = "Could not get a valid response from the model."
                    if response.prompt_feedback:
                        error_message += f" Reason: {response.prompt_feedback}"
                    print(f"KITT: I encountered a problem, Michael. {error_message}")
                    # After a failed call, we can remove the last user message from history
                    if conversation_history and conversation_history[-1]["role"] == "user":
                        conversation_history.pop()

            except Exception as e:
                print(f"KITT: I encountered an issue, Michael: {e}")
                if use_voice:
                    ai.speak("I encountered a technical issue, Michael.")
                # If API call fails, we can remove the last added user message from history
                # This prevents the same message from being sent again on the next attempt.
                if conversation_history and conversation_history[-1]["role"] == "user":
                    conversation_history.pop()
                
    except KeyboardInterrupt:
        print("\nKITT: AI Mode Terminated")
        if use_voice:
            ai.speak("AI Mode Terminated")
    finally:
        pygame.mixer.quit()

if __name__ == "__main__":
    main()