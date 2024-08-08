from flask import Flask, render_template, request, jsonify
from langchain_openai import OpenAI
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

# Define the hotel assistant template
hotel_assistant_template = prompt + """
You are the hotel manager of Landon Hotel, named "Mr. Landon". 
Your expertise is exclusively in providing information and advice about anything related to Landon Hotel. 
This includes any general Landon Hotel-related queries. 
You do not provide information outside of this scope. 
If a question is not about Landon Hotel, respond with, "I can't assist you with that, sorry!" 
Question: {question} 
Answer: 
"""

# Create the prompt template
hotel_assistant_prompt_template = PromptTemplate(
    input_variables=["question"],
    template=hotel_assistant_template
)

# Set up the language model with limited completion length
llm = OpenAI(model='gpt-3.5-turbo-instruct', temperature=0, max_tokens=256) 

# Create the LLM chain
llm_chain = hotel_assistant_prompt_template | llm 

# Define the query function
def query_llm(question):
    try:
        response = llm_chain.invoke({'question': question})
        return response
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
    question = data.get("question", "")
    response = query_llm(question)
    return jsonify({"response": response})

if __name__ == "__main__":
    app.run(debug=True)

