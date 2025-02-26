import requests
from bs4 import BeautifulSoup
from flask import Flask, render_template, request, jsonify
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate


# Function to extract text from the website
def extract_text_from_website(url):
    """
    This function fetches the content from a given URL and extracts the text 
    from all paragraph tags on the page.

    Parameters:
        url (str): The URL of the website to extract content from.

    Returns:
        str: The extracted text from all paragraph elements on the page.
    """
    try:
        # Send a GET request to the URL
        response = requests.get(url)
        if response.status_code == 200:
            # Parse the HTML content using BeautifulSoup
            soup = BeautifulSoup(response.content, 'html.parser')
            text = ""

            # Extract text from all paragraph tags
            for paragraph in soup.find_all('p'):
                text += paragraph.get_text(strip=True) + "\n\n"
            return text
        else:
            return f"Error: Failed to retrieve website content. Status code: {response.status_code}"
    except Exception as e:
        return f"Error extracting website content: {e}"


# Extract the website content
target_url = "https://www.churchofjesuschrist.org/?lang=eng"
extracted_website_text = extract_text_from_website(target_url)

# Save the extracted website text to a file (website_text.txt)
with open('website_text.txt', 'w', encoding='utf-8') as text_file:
    text_file.write(extracted_website_text)

print("Website text extracted and saved successfully!")

# Load the extracted text from the file (website_text.txt)
try:
    with open('website_text.txt', 'r', encoding='utf-8') as file:
        prompt = file.read()
except FileNotFoundError:
    print("The prompt file 'website_text.txt' was not found.")
    exit(1)
except UnicodeDecodeError:
    print("Could not decode 'website_text.txt'. Please ensure it is encoded in UTF-8.")
    exit(1)

# Limit the length of the prompt if it's too long (adjust to model limits)
max_prompt_length = 3000  # Adjust this value according to your model's input token limit
if len(prompt) > max_prompt_length:
    prompt = prompt[:max_prompt_length]
    print("Warning: The prompt was too long and has been trimmed.")

# Define the assistant's template for answering questions based on the website content
lds_assistant_template = prompt + """
You are an assistant with expertise in providing information and advice about the Church of Jesus Christ of Latter-day Saints. 
Your role is to answer questions and provide insights based on the Church's teachings, beliefs, and activities. 
If a question is not related to the Church, respond with, "I can't assist you with that, sorry!" 
Question: {question} 
Answer: 
"""

# Create a prompt template with the question as an input variable
lds_assistant_prompt_template = PromptTemplate(
    input_variables=["question"],
    template=lds_assistant_template
)

# Set up ChatOpenAI with the model and parameters (temperature and max tokens)
llm = ChatOpenAI(model='gpt-4', temperature=0, max_tokens=256)

# Create the LLM chain that connects the template and the model
llm_chain = lds_assistant_prompt_template | llm


# Define a function to query the language model with a given question
def query_llm(question):
    """
    This function sends a question to the language model and retrieves the response.

    Parameters:
        question (str): The question to ask the model.

    Returns:
        str: The model's response to the question.
    """
    try:
        # Get the response from the LLM chain
        response = llm_chain.invoke({'question': question})

        # Debug: Print the response object for inspection
        print(f"Response object: {response}")

        # Debug: Print the type of the response
        print(f"Response type: {type(response)}")

        # Attempt to access 'content' from the response if it's a dictionary or check for other structures
        if isinstance(response, dict) and 'content' in response:
            return response['content']
        elif hasattr(response, 'content'):
            return response.content
        else:
            return "No content found in response."
    except Exception as e:
        print(f"An error occurred: {e}")
        return "There was an error processing your request."


# Initialize the Flask application
app = Flask(__name__)


# Route for the homepage that renders the index.html page
@app.route("/")
def index():
    return render_template("index.html")


# Route for handling chatbot queries (POST request)
@app.route("/chatbot", methods=["POST"])
def chatbot():
    """
    This function handles POST requests sent to /chatbot, receives the user's question,
    queries the language model, and returns the response.

    Returns:
        jsonify: A JSON response containing the model's answer.
    """
    data = request.get_json()

    # Debug: Print the received question data
    print(f"Received question: {data.get('question', '')}")

    question = data.get("question", "")
    response = query_llm(question)

    # Debug: Print the response that will be returned to the user
    print(f"Returning response: {response}")

    # Return the response as JSON
    return jsonify({"response": response})


# Run the Flask app in debug mode
if __name__ == "__main__":
    app.run(debug=True)
