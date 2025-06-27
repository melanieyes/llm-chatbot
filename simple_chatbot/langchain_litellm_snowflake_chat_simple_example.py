from dotenv import load_dotenv
import os
from langchain_litellm import ChatLiteLLM
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

load_dotenv()

# Constants
MODEL_NAME = "snowflake/mistral-7b"

def setup_snowflake_credentials():
    """Set up Snowflake credentials from environment variables"""
    required_vars = [
        "SNOWFLAKE_JWT",  # JWT token for authentication
        "SNOWFLAKE_ACCOUNT_ID"  # Account identifier
    ]
    
    # Check if all required variables are set
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    if missing_vars:
        raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
    
    # Return credentials from environment variables
    return {
        "jwt": os.environ["SNOWFLAKE_JWT"],
        "account_id": os.environ["SNOWFLAKE_ACCOUNT_ID"]
    }

def get_single_llm_response(prompt: str, credentials: dict, model: str = MODEL_NAME):
    try:
        # Initialize the LiteLLM chat model with Snowflake Cortex
        llm = ChatLiteLLM(
            model=model,
            temperature=0.7,
            max_tokens=500,
            api_key=credentials["jwt"],  # Use JWT token as API key
            api_base=f"https://{credentials['account_id']}.snowflakecomputing.com/api/v2/cortex/inference:complete"
        )
        
        # Create a simple prompt with just the user message
        messages = [
            HumanMessage(content=prompt)
        ]
        
        print(f"HumanMessage sent to LLM: {messages}")

        # Get response
        response = llm.invoke(messages)
        print(f"Full Response from LLM: {response}")
        
        return response.content
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

def get_llm_response_with_context(prompt: str, system_prompt: str, credentials: dict, model: str = MODEL_NAME):
    try:
        # Initialize the LiteLLM chat model with Snowflake Cortex
        llm = ChatLiteLLM(
            model=model,
            temperature=0.7,
            max_tokens=500,
            api_key=credentials["jwt"],  # Use JWT token as API key
            api_base=f"https://{credentials['account_id']}.snowflakecomputing.com/api/v2/cortex/inference:complete"
        )
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=prompt)
        ]
        
        # Get response
        response = llm.invoke(messages)
        print(f"Full Response from LLM: {response}")
        
        return response.content
    except Exception as e:
        print(f"Error: {str(e)}")
        return None
    
if __name__ == "__main__":
    try:
        # Set up Snowflake credentials
        print("Setting up Snowflake credentials...")
        credentials = setup_snowflake_credentials()
        
        user_prompt = 'Hello, how are you?'
        system_prompt = "You are a helpful assistant that provides concise and accurate answers to user queries."
        
        print("\nTesting single message response...")
        answer_single = get_single_llm_response(user_prompt, credentials)
        
        print("\nTesting response with context...")
        answer_with_context = get_llm_response_with_context(user_prompt, system_prompt, credentials)
        
        print(f'\nUser prompt: {user_prompt}') 
        print(f'Answer with no context: {answer_single}')
        print(f'Answer with context: {answer_with_context}')
        
    except Exception as e:
        print(f"Error initializing chatbot: {str(e)}")
        print("Please check your Snowflake credentials and try again")