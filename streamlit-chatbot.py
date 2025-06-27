import streamlit as st
import os
from dotenv import load_dotenv  # Used for loading environment variables
from langchain_litellm import ChatLiteLLM
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langgraph.graph import StateGraph, END, START
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph.message import MessagesState
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import uuid

# Load environment variables from .env file at the very beginning
load_dotenv()

# --- Configuration Constants ---
MODEL_NAME = "gpt-3.5-turbo"  # Default LLM model name
SYSTEM_PROMPT = """You are Melanie's AI assistant. Keep your responses concise and friendly. Introduce yourself and ask for the user's name."""

# --- LangChain/LangGraph Setup ---

# Define the chat prompt template, including a system prompt and a placeholder for messages.
# This allows the model to maintain context of the conversation.
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", SYSTEM_PROMPT),
        MessagesPlaceholder(variable_name="messages"),
    ]
)


def create_chatbot_app(model: str = MODEL_NAME):
    """
    Creates and compiles a LangGraph chatbot application.

    Args:
        model (str): The name of the language model to use (e.g., "gpt-3.5-turbo").

    Returns:
        StateGraph: A compiled LangGraph application with memory.
    """
    # Initialize the Language Model (LLM) using ChatLiteLLM.
    # temperature=0.7 makes the responses slightly more creative/less deterministic.
    llm = ChatLiteLLM(model=model, temperature=0.7)

    # Initialize a StateGraph with MessagesState, which handles conversation history.
    workflow = StateGraph(state_schema=MessagesState)

    # Define the function that calls the LLM.
    def call_model(state: MessagesState):
        """
        Invokes the language model with the current conversation state.

        Args:
            state (MessagesState): The current state of the conversation,
                                   containing a list of messages.

        Returns:
            dict: A dictionary containing the updated messages state with the AI's response.
        """
        # Format the messages from the state using the defined prompt template.
        formatted_prompt = prompt.format_messages(messages=state["messages"])

        # Invoke the LLM with the formatted prompt to get a response.
        response = llm.invoke(formatted_prompt)

        # Return the new state, adding the AI's response to the messages list.
        return {"messages": response}

    # Add the 'model' node to the workflow, which executes the call_model function.
    workflow.add_node("model", call_model)

    # Define the flow of the graph:
    # START -> 'model' node -> END
    workflow.add_edge(START, "model")
    workflow.add_edge("model", END)

    # Compile the workflow with a MemorySaver checkpointer.
    # This allows the conversation history to be managed internally by LangGraph.
    memory = MemorySaver()
    app = workflow.compile(checkpointer=memory)
    return app


# --- Streamlit Application Logic ---

# Set the title of the Streamlit app
st.set_page_config(page_title="Melanie's AI Assistant", layout="centered")
st.title("Melanie's AI Assistant")

# --- Session State Initialization ---
# Initialize session state variables if they don't already exist.
# Streamlit reruns the script from top to bottom on every interaction,
# so session_state is crucial for preserving data.

if "messages" not in st.session_state:
    # 'messages' will store the entire conversation history for display.
    st.session_state.messages = []

if "chatbot_app" not in st.session_state:
    # 'chatbot_app' will hold the LangGraph application instance.
    st.session_state.chatbot_app = None

if "thread_id" not in st.session_state:
    # 'thread_id' is used by LangGraph's MemorySaver to track specific conversations.
    st.session_state.thread_id = str(uuid.uuid4())

if "api_key_set" not in st.session_state:
    # 'api_key_set' tracks whether the OpenAI API key has been found.
    st.session_state.api_key_set = False

# --- API Key Check ---
# Check if the OPENAI_API_KEY environment variable is set.
# This is crucial for the LiteLLM model to function.
if not os.getenv("OPENAI_API_KEY"):
    st.warning(
        "Please set your `OPENAI_API_KEY` environment variable in a `.env` file or as a secret."
    )
    st.session_state.api_key_set = False
else:
    st.session_state.api_key_set = True
    # If the API key is set and the chatbot hasn't been initialized yet, do so.
    if st.session_state.chatbot_app is None:
        st.session_state.chatbot_app = create_chatbot_app()
        # Add an initial greeting from the AI assistant
        initial_ai_message = AIMessage(
            content="Hello! I'm Melanie's AI assistant. What's your name?"
        )
        st.session_state.messages.append(
            {"role": "assistant", "content": initial_ai_message.content}
        )


# --- Helper Functions for UI Actions ---


def clear_conversation():
    """
    Clears the conversation history and resets the chatbot,
    effectively starting a new conversation thread.
    """
    st.session_state.messages = []
    st.session_state.thread_id = str(
        uuid.uuid4()
    )  # Generate a new thread ID for the new conversation
    # Re-initialize the chatbot app to ensure clean state with the new thread ID if needed.
    # However, LangGraph's checkpointer uses the thread_id config, so re-initializing app itself is not strictly necessary for clearing memory within LangGraph.
    # It's good practice to ensure consistency or if stateful nodes were outside checkpointer.
    st.session_state.chatbot_app = create_chatbot_app()
    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": "Hello! I'm Melanie's AI assistant. What's your name?",
        }
    )
    st.success("Conversation history cleared!")


def display_help_info():
    """Displays help information in an expander."""
    with st.expander("Commands Help"):
        st.markdown(
            """
            * **Just type your message!** The assistant will respond.
            * **Clear Chat:** Click the 'Clear Conversation' button below.
            * **Model Info:** Click the 'Show Current Model' button below.
            """
        )


def display_model_info():
    """Displays the current model name in an info box."""
    st.info(f"Current model in use: **{MODEL_NAME}**")


# --- Display Chat Messages ---
# Iterate through the messages stored in session_state and display them.
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- User Input and Chat Logic ---

# This creates a text input field at the bottom of the chat.
# `key="chat_input"` is important to uniquely identify this widget across reruns.
# `on_submit` is used to trigger a function when the user presses Enter.
user_input = st.chat_input("Type your message here...", key="chat_input")

if user_input and st.session_state.api_key_set:
    # Add user message to session state for display
    st.session_state.messages.append({"role": "user", "content": user_input})
    # Display the user message immediately
    with st.chat_message("user"):
        st.markdown(user_input)

    try:
        # Create an input message for the LangGraph chatbot
        input_messages = [HumanMessage(content=user_input)]

        # Invoke the chatbot with the user's message and the current thread ID.
        # The thread_id ensures conversation memory is maintained.
        result = st.session_state.chatbot_app.invoke(
            {"messages": input_messages},
            config={"configurable": {"thread_id": st.session_state.thread_id}},
        )

        # Extract the AI's response from the result
        if result and "messages" in result and result["messages"]:
            ai_response_content = result["messages"][-1].content
            # Add AI response to session state for display
            st.session_state.messages.append(
                {"role": "assistant", "content": ai_response_content}
            )
            # Display the AI response
            with st.chat_message("assistant"):
                st.markdown(ai_response_content)
        else:
            st.error("No response received from the AI assistant. Please try again.")

    except Exception as e:
        st.error(f"An error occurred: {e}")
        st.warning("Please check your API key and try again.")
elif user_input and not st.session_state.api_key_set:
    st.error(
        "Cannot send message: OpenAI API Key is not set. Please set it to proceed."
    )


# --- Control Buttons ---
# Layout buttons in columns for a cleaner look
col1, col2, col3 = st.columns(3)

with col1:
    st.button("Clear Conversation", on_click=clear_conversation)
with col2:
    st.button("Show Current Model", on_click=display_model_info)
with col3:
    st.button("Help", on_click=display_help_info)


# Display current thread ID for debugging/information
st.caption(f"Current Chat Session ID: `{st.session_state.thread_id}`")
