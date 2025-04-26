# 🤖 WhatsApp Assistant: Automated CRM & Event Management

An intelligent assistant that monitors your WhatsApp conversations, builds a personal CRM, and schedules events without any manual intervention.

## 📋 Overview

WhatsApp Assistant silently works in the background to:

- 📊 **Extract and organize contact information** into a personal CRM
- 📅 **Detect event mentions** and automatically create calendar entries
- 🗺️ **Integrate location data** from conversation contexts using Google Maps
- 🔄 **Process conversations in real-time** with minimal resource usage

## 🛠️ Technical Architecture

This project leverages several advanced technologies:

- **Model Context Protocol (MCP)** for service integration
- **LangChain ReAct agents** for intelligent processing
- **Async processing** with Python's asyncio
- **Multi-language integration** (Python, Go, JavaScript)
- **Structured data storage** in JSON format

## ⚙️ Installation

### Prerequisites

- Python 3.13
- Node.js 16+
- uv package manager
- Google API credentials (Maps and Calendar)
- OpenAI credentials

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/whatsapp-assistant.git
   cd whatsapp-assistant
   ```

2. Install dependencies with uv:
   ```bash
   uv venv
   uv pip install -r requirements.txt
   ```

3. Set up environment variables:
   ```bash
   export GOOGLE_API_KEY="your-google-api-key"
   export OPENAI_API_KEY="your-openai-api-key"
   ```

4. Install WhatsApp MCP server:
   ```

5. Install Google Calendar MCP server: 

6. Install Google Maps MCP Server: 

7. Change the paths in main.py to reflect the new path.
## 🚀 Usage

1. Start the assistant:
   ```bash
   python main.py
   ```

2. The assistant will run in the background, monitoring your WhatsApp conversations and automatically:
   - Building and updating CRM entries in the `crm/` directory
   - Creating calendar events when detected in conversations
   - Logging activities to `output.txt`

3. You can interact with the assistant directly:
   ```
   User: What do you know about John?
   ```

## 📁 Project Structure

```
whatsapp-assistant/
├── main.py                  # Main application entry point
├── crm/                     # Directory for CRM data storage
├── whatsapp_mcp_server/     # WhatsApp MCP implementation
├── google-calendar-mcp/     # Google Calendar MCP implementation
└── output.txt               # Log of assistant activities
```

## 🧩 Key Components

### CRM Agent

Extracts personal information from conve