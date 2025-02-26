from flask import Flask, render_template, request, jsonify
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate

# Load and check the prompt size from the file with explicit encoding
try:
    with open('website_text.txt', 'r', encoding='utf-8') as file:
        prompt = file.read()
except FileNotFoundError:
    print("The prompt file 'website_text.txt' was not found.")
    exit(1)
except UnicodeDecodeError:
    print("Could not decode 'website_text.txt'. Please ensure it is encoded in UTF-8.")
    exit(1)

# Limit the prompt length if it's too long
max_prompt_length = 3000  # Adjust this to fit within model limits
if len(prompt) > max_prompt_length:
    prompt = prompt[:max_prompt_length]
    print("Warning: The prompt was too long and has been trimmed.")

# Define the LDS assistant template
lds_assistant_template = prompt + """
You are an assistant with expertise in providing information and advice about the Church of Jesus Christ of Latter-day Saints. 
Your role is to answer questions and provide insights based on the Church's teachings, beliefs, and activities. 
If a question is not related to the Church, respond with, "I can't assist you with that, sorry!" 
Question: {question} 
Answer: 
"""

# Create the prompt template
lds_assistant_prompt_template = PromptTemplate(
    input_variables=["question"],
    template=lds_assistant_template
)

# Use ChatOpenAI (correct model setup for chat models like gpt-3.5-turbo)
llm = ChatOpenAI(model='gpt-4', temperature=0, max_tokens=256)

# Create the LLM chain
llm_chain = lds_assistant_prompt_template | llm


# Define the query function
def query_llm(question):
    try:
        # Get the response from the LLM chain
        response = llm_chain.invoke({'question': question})
        
        # Debug: Print the entire response object
        print(f"Response object: {response}")
        
        # Print the type of the response
        print(f"Response type: {type(response)}")
        
        # Attempt to access 'content' if it's a dict or check other possible structures
        if isinstance(response, dict) and 'content' in response:
            return response['content']
        elif hasattr(response, 'content'):
            return response.content
        else:
            return "No content found in response."
    except Exception as e:
        print(f"An error occurred: {e}")
        return "There was an error processing your request."


# Initialize Flask app
app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/chatbot", methods=["POST"])
def chatbot():
    data = request.get_json()
    
    # Debug: Print the incoming data
    print(f"Received question: {data.get('question', '')}")
    
    question = data.get("question", "")
    response = query_llm(question)
    
    # Debug: Print the response that will be returned
    print(f"Returning response: {response}")
    
    return jsonify({"response": response})


if __name__ == "__main__":
    app.run(debug=True)
