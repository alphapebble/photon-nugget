# 🌞 Solar-Sage: Intelligent Solar Energy Assistant

Solar-Sage is a domain-aware AI assistant designed to support engineers, site operators, and analysts in the solar energy lifecycle — from site planning to QA audits and performance diagnostics. Powered by LLMs and integrated with geospatial pipelines (e.g., point cloud analysis, CAD deviation detection, thermal anomaly classification), it answers questions, explains results, and guides workflows through a conversational interface.

![Solar-Sage Screenshot](https://github.com/balijepalli/solar-sage/raw/main/docs/images/screenshot.png)

## 🌟 What Can It Do?

- Answer questions about solar panels, installation, and energy
- Work completely offline on your computer
- Provide accurate information from reliable solar energy sources
- Remember your conversation history
- Switch between light and dark mode for comfortable viewing

## 🚀 Quick Start Guide (For Everyone)

### Prerequisites

Before you begin, make sure you have:

1. **Python 3.9+** installed on your computer
   - [Download Python](https://www.python.org/downloads/) if you don't have it

2. **Git** to download the project
   - [Download Git](https://git-scm.com/downloads) if you don't have it

### Step 1: Download the Project

Open your terminal (Command Prompt on Windows) and run:

```bash
git clone https://github.com/balijepalli/solar-sage.git
cd solar-sage
```

### Step 2: Set Up the Environment

Create a virtual environment and install the required packages:

```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install required packages
pip install -r requirements.txt
```

### Step 3: Start the Backend Server

Open a new terminal window, navigate to the project folder, activate the virtual environment, and run:

```bash
# On Windows:
set USE_OLLAMA=true
set MODEL_NAME=mistral
python -m app.server

# On macOS/Linux:
USE_OLLAMA=true MODEL_NAME=mistral python -m app.server
```

Keep this terminal window open while using the application.

### Step 4: Start the User Interface

Open another terminal window, navigate to the project folder, activate the virtual environment, and run:

```bash
python -m ui.app
```

This will start the web interface. You'll see a URL like `http://0.0.0.0:8502` or `http://127.0.0.1:8502` in the terminal.

### Step 5: Use the Application

1. Open your web browser and go to the URL shown in the terminal (usually http://127.0.0.1:8502)
2. Type your solar energy question in the text box
3. Click "Ask" or press Enter to get an answer
4. Enjoy your conversation with the AI assistant!

## 🔍 Using Advanced Features

### Dark Mode

Click the "Toggle Dark Mode" button to switch between light and dark themes.

### Conversation History

- **Save History**: Click "Save History" to save your current conversation
- **Load History**: Click "Load History" to restore a previously saved conversation
- **Clear Chat**: Click "Clear Chat" to start a new conversation

### Feedback

After receiving an answer, you can provide feedback by clicking:
- 👍 Yes - if the answer was helpful
- 👎 No - if the answer wasn't helpful

## 🛠️ Troubleshooting

### Common Issues and Solutions

1. **"Connection Error" when asking a question**
   - Make sure the backend server is running (Step 3)
   - Check that you're using the correct URL in your browser

2. **"Module not found" errors**
   - Make sure you've activated the virtual environment
   - Try reinstalling the requirements: `pip install -r requirements.txt`

3. **Slow responses**
   - The AI model needs time to think, especially on the first question
   - Responses should get faster after the first few questions

4. **Application crashes or freezes**
   - Restart both the backend server and the UI
   - Make sure your computer meets the minimum requirements

### Getting Help

If you encounter problems not covered here:
1. Check the [GitHub Issues](https://github.com/balijepalli/solar-sage/issues) page
2. Create a new issue with details about your problem

## 📚 For Developers

If you're a developer interested in the technical details or want to contribute to the project, check out the [Developer Documentation](docs/DEVELOPERS.md).

### Project Structure

```
solar-sage/
├── app/                # Backend server
├── ui/                 # Frontend interface
├── rag/                # Retrieval system
├── llm/                # AI model integration
├── retriever/          # Document retrieval
├── models/             # AI models
└── data/               # Knowledge database
```

### Running with Different Models

You can use different AI models by changing the `MODEL_NAME` parameter:

```bash
# Using Mistral model
USE_OLLAMA=true MODEL_NAME=mistral python -m app.server

# Using Llama model
USE_OLLAMA=true MODEL_NAME=llama python -m app.server
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [Gradio](https://gradio.app/) for the user interface
- Powered by [Mistral AI](https://mistral.ai/) models
- Uses [LanceDB](https://lancedb.github.io/lancedb/) for knowledge retrieval
