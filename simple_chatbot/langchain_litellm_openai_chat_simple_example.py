from dotenv import load_dotenv
import os
from langchain_litellm import ChatLiteLLM
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

load_dotenv()

# Constants
MODEL_NAME = "gpt-3.5-turbo"

def get_single_llm_response(prompt: str, model: str = MODEL_NAME):
    try:
        # Initialize the LiteLLM chat model
        llm = ChatLiteLLM(
            model=model,
            temperature=0.7,
            max_tokens=500
        )
        
        # Create a simple prompt with just the user message. We'll leave the system message blank.
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

def get_llm_response_with_context(prompt: str, system_prompt: str, model: str = MODEL_NAME):
    try:
        # Initialize the LiteLLM chat model
        llm = ChatLiteLLM(
            model=model,
            temperature=0.7,
            max_tokens=500
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
    user_prompt = 'Hello, how are you?'
    system_prompt = "You are a helpful assistant that provides concise and accurate answers to user queries."
    answer_with_context = get_llm_response_with_context(user_prompt, system_prompt)
    print(f'User prompt: {user_prompt}') 
    print(f'Answer with no context: {answer_single}')
    print(f'Answer with context: {answer_with_context}')