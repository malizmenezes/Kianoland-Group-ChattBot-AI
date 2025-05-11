# Kianoland Group ChattBot AI 🤖

A multi-platform chatbot for property consultations, integrated with Any Website Discord and Telegram using Dialogflow ES for natural language processing.

## Features ✨

- **Multi-platform support**: Website, Discord and Telegram
- **Natural Language Processing**: Powered by Dialogflow ES
- **Dedicated channels**: Keeps bot interactions organized
- **Thread isolation**: Private consultations in separate threads

## Setup Instructions 🛠️

### Prerequisites

- Python 3.8+
- Discord Bot Token
- Telegram Bot Token
- Google Cloud Service Account JSON

### Installation

Clone the repository:

```bash
git clone https://github.com/fatonyahmadfauzi/Kianoland-Group-ChattBot-AI.git
cd Kianoland-Group-ChattBot-AI
```

## Setup Instructions 🛠️

### Backend Setup

1. Navigate to backend folder:
   ```bash
   cd backend
   ```
2. Create and activate virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows   cd Kianoland-Group-ChattBot-AI
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Create `.env` file:
   ```bash
   cp .env.example .env
   ```
   Then edit `.env` with your credentials.

### Configuration

Fill in your `.env` file:

```env
DISCORD_TOKEN=your_discord_token_here
TELEGRAM_TOKEN=your_telegram_token_here
DIALOGFLOW_PROJECT_ID=your_project_id
DEDICATED_CHANNEL_ID=your_channel_id
GOOGLE_APPLICATION_CREDENTIALS=service-account.json
```

### Frontend Setup

1. Open `frontend/index.html` in your browser
2. No additional setup required for static files

### Running the Bot

```bash
uvicorn app:app --reload --port 8000
```

## Project Structure 📁

```bash
Kianoland-Group-ChattBot-AI
├── backend/
│   ├── __pycache__
│   ├── __init__.py
│   ├── app.py                    # Main FastAPI application
│   ├── dialogflow_integration.py # Dialogflow integration
│   ├── requirements.txt          # Python dependencies
│   └── service-account.json      # Google Cloud credentials
├── frontend/
│   ├── index.html                # Main HTML file
│   ├── script.js                 # Frontend JavaScript
│   └── style.css                 # CSS styles
├── __init__.py
├── .env                          # Environment
├── app.py                        # Main application
├── .gitignore
├── LICENSE
└── README.md                     # This file
```

## Bot Commands 🤖

### Discord

- `!info` - Get property information
- `!konsul [question]` - Start private consultation
- Mention bot in other channels to get redirected

### Telegram & Website

Just send messages normally

## Troubleshooting 🔧

- **Privileged Intents Error**: Enable intents in [Discord Developer Portal](https://discord.com/developers)
- **Dialogflow Authentication**: Ensure `service-account.json` is in root directory
- **Port Conflicts**: Change port in run command if 8000 is occupied

## License 📄

This project is licensed under the MIT License.
