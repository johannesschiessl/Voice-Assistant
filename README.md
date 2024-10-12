# Voice-Assistant

A basic voice assistant that can be run in the terminal and interacts with you through voice commands and responses. It allows you to have simple conversations and perform basic tasks using natural language.

## Getting Started

### Installation

1. Clone this repository:

   ```bash
   git clone https://github.com/johannesschiessl/Voice-Assistant.git
   cd voice-assistant
   ```

2. Install the required Python libraries:

   ```bash
   pip install -r requirements.txt
   ```

3. Rename `.env.example` to `.env` and add your API keys:

   ```
   OPENAI_API_KEY=your_openai_key
   GROQ_API_KEY=your_groq_key
   ```

   You can obtain the keys from [OpenAI Platform](https://platform.openai.com) and [Groq Console](https://console.groq.com).

### Usage

Run the main script to start the assistant:

```bash
python src/main.py
```

The assistant listens for voice commands and processes them in real-time, providing responses through TTS (Text-to-Speech).

## Project Structure

- **src/**: Contains the core logic of the assistant.
  - `main.py`: Entry point of the project.
- **requirements.txt**: Python dependencies for the project.

## Contributing

Feel free to contribute by creating issues or pull requests. Suggestions for new features are always welcome!

## Future Plans

- **Run on Raspberry Pi**: Make the assistant fully functional on a Raspberry Pi for a portable, always-on voice assistant.

- **Web Search Capabilities**: Add the ability to perform web searches to answer user queries more comprehensively.

- **Tools like Timer and Alarm**: Implement features like setting timers and alarms to make the assistant more useful for day-to-day tasks.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
