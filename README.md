# LangChain + LiteLLM Chatbot Examples

## 🧠 Overview

This repository showcases simple and advanced use cases of [LangChain](https://www.langchain.com/) with [LiteLLM](https://github.com/BerriAI/litellm) for building conversational AI applications. The examples range from minimal prompt-response interactions to stateful chatbots with memory, and even include integration with **Snowflake Cortex** for enterprise-level use.

---

## 📁 Project Structure

### `langchain_litellm_openai_chat_simple_example.py`

A minimal example demonstrating how to:

- Send a single prompt to an OpenAI model (e.g., `gpt-3.5-turbo`)
- Use contextual prompts with `SystemMessage`
- Handle errors gracefully

🔹 **Ideal for**: basic testing and API exploration.

---

### `langchain_litellm_openai_chatbot_example.py`

A command-line chatbot with:

- `LangGraph` for managing conversation flow
- `MessagesState` and `MemorySaver` for memory
- Interactive CLI features using `rich`

🔹 **Available commands**:
- `help` – Show help message  
- `clear` – Clear conversation history  
- `model` – Display current model  
- `quit` / `exit` – Exit session

🔹 **Ideal for**: building conversational agents with memory.

---

### `langchain_litellm_snowflake_chat_simple_example.py`

A simple chat example using **Snowflake Cortex LLMs**, integrating:

- JWT-based authentication
- Custom API endpoint via Snowflake
- LangChain + LiteLLM

🔹 **Environment variables required**:
- `SNOWFLAKE_JWT`
- `SNOWFLAKE_ACCOUNT_ID`

🔹 **Ideal for**: secure enterprise chat solutions.

---

## ⚙️ Setup Instructions

### 1. Install Dependencies

Install with `requirements.txt`:

```bash
pip install -r requirements.txt
