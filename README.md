# 🚗 AI Parking Analyst (Full-Stack MCP System)

A **Model Context Protocol (MCP)** ecosystem that transforms raw WhatsApp location data into a predictive parking assistant. This project bridges a high-performance **Go** ingestion layer with a **Python** heuristic analysis engine, allowing an AI (like Claude) to act as a personal parking consultant.

## 🌟 The "Why"
In Tel Aviv, finding a parking spot is a notorious daily struggle. With high demand and complex municipal regulations, the search for a spot can often take longer than the drive itself.

I built this project to turn that frustration into a data-driven advantage. By leveraging the history of a shared WhatsApp parking group, this system:

Analyzes Patterns: Identifies exactly where and when I park most often.

Optimizes the Hunt: Uses historical data to predict which streets are likely to have openings at specific times.

Actionable Insights: Converts messy, unstructured Hebrew chat messages into a context-aware recommendation engine, helping me (and Nir) navigate the Tel Aviv parking maze more efficiently.

## 🏗️ System Architecture
The project is organized as a **Monorepo**, utilizing a shared SQLite database to bridge two distinct runtime environments:

1.  **Data Ingestion (Go):** * A high-concurrency WhatsApp bridge using the `whatsmeow` framework.
    * Implements strict **JID filtering** to ensure only relevant parking group data is stored.
    * Manages a local SQLite database with automated schema initialization.

2.  **Analysis Engine (Python 3.12):**
    * **Semantic Normalization:** Custom regex-based cleaning of Hebrew address strings (e.g., "הפרדס 10" → "הפרדס").
    * **Heuristic Modeling:** A tiered "Confidence-First" algorithm that predicts the best parking spot based on temporal patterns (Day of Week + Time Window).
    * **MCP Server:** Exposes the analysis logic to LLMs via the Model Context Protocol.

## 🛠️ Tech Stack
* **Languages:** Go (Golang), Python 3.12
* **Database:** SQLite
* **Protocol:** Model Context Protocol (MCP)
* **Key Libraries:** `whatsmeow` (Go), `fastmcp` (Python), `python-dotenv`, `godotenv`

## 🚀 Setup & Installation

### 1. Configure Environment
Create a `.env` file in the root directory. This ensures security by keeping private Group IDs and local file paths out of version control.
```env
PARKING_GROUP_JID="12036302345678@g.us"
DB_PATH="/Users/yourname/projects/parking-analyst/whatsapp-bridge/store/messages.db"
```

### 2. Run the WhatsApp Bridge (Go)
```bash
cd whatsapp-bridge
go run main.go
```
*On the first run, scan the QR code in the terminal with your WhatsApp app to link the session.*

### 3. Run the Analyst (Python)
```bash
cd parking-analyst
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python parking_server.py
```

## 🧠 Technical Challenges Solved
* **Cross-Language Configuration:** Synchronized a Go backend and Python frontend by implementing `godotenv` and `python-dotenv` to share a single source of truth (`.env`).
* **Data Integrity & Filtering:** Modified the open-source bridge to include a targeted filter, preventing database "noise" from non-parking-related WhatsApp chats.
* **Heuristic Logic:** Developed a three-tier fallback system for parking recommendations:
    1.  **Perfect Match:** Same day and same hour window.
    2.  **Temporal Match:** Any day within the same hour window.
    3.  **Historical Baseline:** Most frequent spot overall.

## ⚖️ Licensing
This project is licensed under the MIT License. 

## 🤝 Credits & Acknowledgements
This project utilizes a modified version of the [whatsapp-mcp bridge](https://github.com/lharries/whatsapp-mcp) by **lharries**. The original ingestion logic was extended to support specific group filtering and enhanced SQLite schema for parking analysis.
This is also licensed under the MIT License. The original license is preserved within that directory.

## 📈 Example Queries
Once connected to Claude, you can ask:
* *"Where should I park right now?"*
* *"Who usually parks more on Ben Ezra street—Sapir or Nir?"*
* *"Where is the best place to park on a Tuesday at 7 PM?"*
* *"What are my most used streets this month?"*

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
