# Knight Rider - K.I.T.T. Simulation

## Overview

This project is a terminal-based simulation inspired by the iconic 80s TV series "Knight Rider." It allows users to interact with K.I.T.T. (Knight Industries Two Thousand), a highly advanced, artificially intelligent car. Users can control K.I.T.T.'s basic functions, engage in conversations, and navigate a simulated road environment with other AI-controlled vehicles. The simulation includes several of K.I.T.T.'s signature features and aims to recreate the feel of the show within a text-based interface.

## Features

* **Interactive K.I.T.T. Control:** Command K.I.T.T. to accelerate, brake, and change lanes.
* **AI-Powered Conversations:** Chat with K.I.T.T., powered by the Google Gemini API, designed to mimic his witty and intelligent persona.
* **Signature Abilities:**
    * **Turbo Boost:** Engage a temporary burst of speed.
    * **Shield Mode:** Activate K.I.T.T.'s protective shield to reduce damage from collisions.
    * **Autopilot:** Let K.I.T.T. manage speed and basic lane-keeping.
    * **Radar:** Scan the vicinity for other AI vehicles.
* **In-Car Music Player:** An interactive music player (using Pygame) to play songs from a local directory.
* **Drift Mini-Game:** Engage in a reaction-time based drift mini-game at designated intersections.
* **Dynamic Road Environment:**
    * Text-based visualization of the road, K.I.T.T., and other AI vehicles.
    * AI-controlled traffic with basic behavior.
    * Collision detection and damage system for K.I.T.T.
* **Scoring System:** Earn points for actions like using Turbo Boost and successful drifts.

## System Design

The simulation is built with a modular approach in Python, with different aspects of the game handled by separate files:

* **Object-Oriented Programming (OOP):** The core design heavily utilizes OOP principles. Classes like `Vehicle`, `KITT`, `Road`, and `MusicPlayer` encapsulate data and behavior, promoting organization and reusability. K.I.T.T. itself is an instance of a class that inherits from a general `Car` class (which in turn inherits from `Vehicle`).

* **Core Modules:**
    * **Main Simulation Engine** (`main_simulation.py`): Acts as the main game engine. It handles the primary simulation loop, parses user commands, and orchestrates interactions between K.I.T.T., the road environment, and other game systems.
    * **Vehicle Definitions** (`vehicles.py`): Defines the base `Vehicle` class and specialized vehicle types like `Car`, `Truck`, and `Motorcycle`. Crucially, it defines the `KITT` class, which inherits from `Car` and incorporates all its unique abilities and attributes (damage, score, shield, turbo, autopilot, AI chat, music player integration, radar, and drift capabilities).
    * **Road & Environment Management** (`road_manager.py`): Manages the road environment, including its length, number of lanes, and the generation and basic behavior of AI-controlled traffic. It's also responsible for the text-based rendering of the road and all vehicles, and manages intersection logic for events like drifts. This module uses `ai_vehicle_config.cfg` for AI vehicle model variety.
    * **K.I.T.T. AI Interface** (`kitt_ai.py`): Integrates with the Google Gemini API to provide K.I.T.T.'s conversational abilities. It manages the conversation history and uses a system prompt to guide the AI's responses to align with K.I.T.T.'s persona, addressing the user as "Michael."
    * **Music Player** (`music_player.py`): Implements an interactive music player using `pygame.mixer`. It allows users to play, stop, pause, and control the volume of music tracks stored locally in a `music` directory. Configuration for this module is handled by `config.json`.
    * **Drift Minigame** (`drift_game.py`): Contains the logic for a standalone, terminal-based reaction time mini-game that is triggered when K.I.T.T. initiates a drift, typically at intersections.
    * **Music Player Configuration** (`config.json`): A JSON file used to configure settings for the `music_player.py` module, such as default volume, supported audio formats, and the music directory path.
    * **AI Vehicle Configuration** (`ai_vehicle_config.cfg`): (Referenced in `road_manager.py`) This file is intended to store configurations for the makes and models of AI vehicles to provide variety in the simulation.

## Key Techniques & Technologies

* **Programming Language:** Python 3
* **Artificial Intelligence:**
    * Google Gemini API (`google-generativeai` library) for natural language understanding and generation, enabling K.I.T.T.'s conversational persona.
    * System prompts are used to define K.I.T.T.'s character and response style.
    * Conversation history management to provide context for ongoing interactions.
* **Audio Playback:**
    * `pygame.mixer` module is used for loading and controlling music playback, providing an in-car entertainment experience.
* **User Interface:**
    * Purely terminal-based, using `print()` for output and `input()` for commands.
    * Text-based graphics are used to render the road, K.I.T.T., and other vehicles.
* **Core Logic & Structure:**
    * **Modular Programming:** Functionality is divided into distinct Python files for better organization and maintainability.
    * **Event Loop:** A central `while` loop in `main_simulation.py` drives the simulation, processing inputs, updating states, and rendering the environment.
    * **State Management:** The simulation carefully tracks the state of K.I.T.T. (e.g., speed, position, damage, active abilities) and the environment.
    * **Randomization:** Used for generating AI traffic, their initial states, and for certain game events (e.g., delays in the drift game).
* **Configuration:**
    * External JSON file (`config.json`) for music player settings, allowing easy modification without code changes.
* **Standard Libraries:** Extensive use of Python's standard libraries including `os`, `time`, `random`, `json`, `pathlib`, `difflib`, and `sys`.

## Setup and Running

1.  **Python Environment:** Ensure you have Python 3 installed.
2.  **Install Dependencies:**
    ```bash
    pip install google-generativeai pygame
    ```
3.  **API Key for K.I.T.T. AI:**
    * You will need a Google Gemini API key.
    * Open `kitt_ai.py` (formerly `AI.py`) and replace the placeholder API key with your actual key:
        ```python
        api_key = "YOUR_ACTUAL_GEMINI_API_KEY" #
        ```
        (It is highly recommended to use environment variables for API keys in real applications for better security.)
4.  **Music Files:**
    * Create a directory named `music` in the same folder as the Python scripts. This is configurable via `config.json`.
    * Place your `.mp3`, `.wav`, or `.ogg` audio files (or other formats specified in `config.json`) into this `music` directory.
5.  **Run the Simulation:**
    ```bash
    python main_simulation.py
    ```

Follow the on-screen prompts to interact with K.I.T.T. and the simulation.
