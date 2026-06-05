# AI Interview Assistant

A lightweight, local, AI-powered technical interview application built with Streamlit, Ollama, and SQLite.

## Features
- **Local AI Engine**: Uses Llama 3 via Ollama for zero-cost, private AI interactions.
- **Dynamic Interviews**: AI generates questions dynamically based on the selected technology and difficulty.
- **Feedback & Scoring**: After 5 questions, the AI analyzes your performance, providing a score out of 10 along with strengths, weaknesses, and improvement suggestions.
- **Dashboard**: Track your past interview scores and history using an SQLite database.
- **Modern UI**: Clean dark theme with responsive layout and cards.

## Prerequisites
1. **Python 3.8+**
2. **Ollama**: You must have Ollama installed on your system. 
   - Download from [Ollama's website](https://ollama.com/)
   - Once installed, open a terminal and run `ollama run llama3` to download the Llama 3 model.

## Installation

1. Navigate to the project directory:
   ```bash
   cd AI-Interview-Assistant
   ```

2. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

Start the Streamlit server:
```bash
streamlit run app.py
```

The application will open in your default web browser (typically at `http://localhost:8501`).

## Project Structure
- `app.py`: Main Streamlit application with UI and Ollama integration.
- `database.py`: SQLite database initialization and operations.
- `styles.css`: Custom UI styling.
- `requirements.txt`: Python dependencies.
