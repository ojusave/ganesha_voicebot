# Interactive Ganesha Voicebot using Deepgram , Cerebras and Cartesia

This project is an interactive voicebot that leverages Deepgram's speech-to-text API, the Cerebras model for response generation, and Cartesia for text-to-speech synthesis. The voicebot provides wisdom and blessings in the style of the Hindu deity Ganesha, offering a unique, immersive experience.

## Features

- **Real-time Audio Processing**: Capture and process audio input in real-time.
- **Speech Recognition**: Leverage Deepgram's API for accurate speech-to-text conversion.
- **AI Response Generation**: Use Cerebras models to generate contextually relevant responses.
- **Text-to-Speech**: Utilize Cartesia for converting text responses into speech, allowing the chatbot to communicate audibly.
- **Customizable Context**: Tailor the chatbot's responses based on user-defined deity contexts.

## Requirements

To run this project, you need to have Python 3.7 or higher installed. You will also need to install the required packages listed in `requirements.txt`.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/ojusave/ganesha_voicebot
   cd ganesha_voicebot
   ```

2. Create a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the root directory of the project and add your API keys (see the sample below).

## API Keys

You will need the following API keys to run the chatbot:

- **Deepgram API Key**: Sign up at [Deepgram](https://deepgram.com/) to obtain your API key.
- **Cerebras API Key**: Sign up at [Cerebras](https://cerebras.net/) to obtain your API key.
- **Cartesia API Key**: Sign up at [Cartesia](https://cartesia.ai/) to obtain your API key.

## .env File

Create a file named `.env` in the root directory of your project and add the following content:


Replace `your_deepgram_api_key`, `your_cerebras_api_key`, and `your_cartesia_api_key` with your actual API keys.

## Running the Application

To start the chatbot, run the following command:

bash

python interactive-chatbot/new.py


Once the application is running, speak into your microphone, and the chatbot will respond with blessings and wisdom.

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue for any suggestions or improvements.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.


Once the application is running, speak into your microphone, and the chatbot will respond with blessings and wisdom.

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue for any suggestions or improvements.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.

## Acknowledgments

This project is inspired by the [Fast Voice Assistant](https://github.com/dsa/fast-voice-assistant) project, which contains everything you need to run your own AI voice assistant that responds to you in less than 500ms.