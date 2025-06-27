from dotenv import load_dotenv
import os
from langchain_litellm import ChatLiteLLM
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langgraph.graph import StateGraph, END, START
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph.message import MessagesState
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import uuid

### Extra beauty fancy stuff that you won't need for your project but I like to have
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.text import Text

# Initialize rich console
console = Console()

# Load environment variables
load_dotenv()

# Constants
MODEL_NAME = "gpt-3.5-turbo"
SYSTEM_PROMPT = """You are a helpful assistant that provides concise and accurate answers to user queries."""

# Create prompt template
prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    MessagesPlaceholder(variable_name="messages"),
])

def create_chatbot(model: str = MODEL_NAME):
    """Create a chatbot instance using LangGraph and LiteLLM"""
    # Initialize the LLM
    llm = ChatLiteLLM(
        model=model,
        temperature=0.7
    )
    
    # Create the workflow
    workflow = StateGraph(state_schema=MessagesState)
    
    # Define the model node
    def call_model(state: MessagesState):
        """Call the model with the current state"""
        # Format messages with prompt template
        formatted_prompt = prompt.format_messages(messages=state["messages"])
        
        # Get response from model
        response = llm.invoke(formatted_prompt)
        
        # Return the updated messages state with the new response
        return {"messages": response}
    
    # Add the model node
    workflow.add_node("model", call_model)
    
    # Add edges
    workflow.add_edge(START, "model")
    workflow.add_edge("model", END)
    
    # Compile the workflow with memory
    memory = MemorySaver()
    app = workflow.compile(checkpointer=memory)
    
    return app

def clear_conversation(conversation):
    """Clear the conversation history"""
    # Create a new conversation instance
    conversation = create_chatbot()
    console.print("[yellow]Conversation history cleared![/yellow]")
    return conversation

def display_help():
    """Display help information"""
    help_text = """
    Available Commands:
    • help - Show this help message
    • quit or exit - Exit the chatbot
    • clear - Clear conversation history
    • model - Show current model
    """
    console.print(Panel(help_text, title="Help", border_style="cyan"))

def main():
    # Check for API key
    if not os.getenv('OPENAI_API_KEY'):
        console.print("[red]Error: Please set your OPENAI_API_KEY environment variable[/red]")
        return
    
    # Create chatbot instance
    conversation = create_chatbot()
    
    # Generate a unique thread ID for this conversation
    current_thread_id = str(uuid.uuid4())
    
    # Welcome message
    console.print(Panel(
        Text("FoundryAI Training Assistant", style="bold cyan"),
        border_style="cyan"
    ))
    console.print(f"[yellow]Current Thread ID: {current_thread_id}[/yellow]")
    console.print("[yellow]Type 'help' for available commands[/yellow]")
    
    while True:
        try:
            # Get user input using standard Python input
            user_input = input("\nYou: ").strip()
            
            if not user_input:
                continue
                
            if user_input.lower() in ['quit', 'exit']:
                console.print("\n[green]Goodbye! Have a great day![/green]")
                break
            elif user_input.lower() == 'clear':
                conversation = clear_conversation(conversation)
                current_thread_id = str(uuid.uuid4())
                console.print(f"[yellow]New Thread ID: {current_thread_id}[/yellow]")
                continue
            elif user_input.lower() == 'model':
                console.print(Panel(
                    f"Current model: {MODEL_NAME}",
                    title="Model Info",
                    border_style="yellow"
                ))
                continue
            elif user_input.lower() == 'help':
                display_help()
                continue
            
            # Create input message
            input_messages = [HumanMessage(content=user_input)]
            
            # Get response from the model with thread ID for memory
            result = conversation.invoke(
                {"messages": input_messages},
                config={"configurable": {"thread_id": current_thread_id}}
            )

            # Print the response
            if result and "messages" in result and result["messages"]:
                console.print("\n[bold green]Assistant:[/bold green]")
                console.print(Markdown(result['messages'][-1].content))
                
        except KeyboardInterrupt:
            console.print("\n\n[green]Goodbye! Have a great day![/green]")
            break
        except Exception as e:
            console.print(f"\n[red]An error occurred: {str(e)}[/red]")
            console.print("[yellow]Please try again or type 'quit' to exit[/yellow]")

if __name__ == "__main__":
    main()
