# 🚗 AI Parking Analyst (MCP Server)

A **Model Context Protocol (MCP)** server that transforms raw WhatsApp location logs into a predictive parking assistant. This project uses a custom-built **Analysis Engine** to help users decide where to park based on historical patterns and real-time context.

## 🏗️ Architecture
The system is built with a decoupled architecture to ensure privacy and data integrity:
1.  **Data Ingestion (Go):** A WhatsApp bridge that listens for messages in a specific "Parking" group and stores them in a local SQLite database.
2.  **Privacy Layer:** Implements JID whitelisting to ensure the AI only accesses authorized group data, maintaining total privacy for personal chats.
3.  **Analysis Engine (Python):** A custom logic layer that performs data normalization (Regex-based address cleaning) and statistical modeling.
4.  **MCP Interface:** Connects the local engine to LLMs (like Claude), allowing for conversational queries about parking habits and predictions.

## 🧠 The Analysis Engine
The center of this project is the **Heuristic Prediction Engine** located in `parking_server.py`. Unlike a simple search, this engine performs:
* **Semantic Normalization:** Uses Regular Expressions to strip house numbers from Hebrew address strings (e.g., "הפרדס 10" → "הפרדס"), allowing for aggregate street-level analysis.
* **Tiered Heuristics:** Employs a "Confidence-First" approach:
    * **High Confidence:** Matches the current Day of Week + 2-hour Time Window.
    * **Medium Confidence:** Matches the 2-hour Time Window across any day.
    * **Fallback:** Provides the global statistical mode (most frequent spot) if no local patterns exist.
* **Multilingual Support:** Native handling of Hebrew UTF-8 strings.

## 🛠️ Features
* `get_parking_recommendation`: Predicts the best spot based on your current time or a future "target" time.
* `get_street_stats`: Provides a frequency report of your most-used streets.
* `get_driver_history`: Returns a detailed log, distinguishing between different drivers (e.g., Sapir vs. Nir).

## 🚀 Setup & Installation

### Prerequisites
* Python 3.10+
* The [WhatsApp-MCP Bridge](https://github.com/lharries/whatsapp-mcp) running locally.

### Installation
1.  **Clone the repository** into your projects folder.
2.  **Create a Virtual Environment**:
    ```bash
    python3 -m venv .venv
    ```
3.  **Activate the Environment**:
    * **Mac/Linux**: `source .venv/bin/activate`
    * **Windows**: `.venv\Scripts\activate`
4.  **Install Dependencies**:
    ```bash
    pip install --upgrade pip
    pip install -r requirements.txt
    ```

### Claude Desktop Configuration
To connect this server to Claude, add the following to your `claude_desktop_config.json`. **Note:** You must point the `command` path specifically to the Python interpreter inside your `.venv`.

```json
{
  "mcpServers": {
    "parking-analyst": {
      "command": "/YOUR_ABSOLUTE_PATH/parking-analyst/.venv/bin/python3",
      "args": [
        "/YOUR_ABSOLUTE_PATH/parking-analyst/parking_server.py"
      ],
      "env": {
        "PYTHONPATH": "/YOUR_ABSOLUTE_PATH/parking-analyst"
      }
    }
  }
}