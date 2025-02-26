import fitz  # PyMuPDF
from flask import Flask, render_template, request, jsonify  # Flask
from langchain_openai import ChatOpenAI  # langchain_openai
from langchain.prompts import PromptTemplate  # langchain.prompts


# Function to extract text from the PDF 
def extract_text_from_pdf(pdf_file_path):
    try:
        doc = fitz.open(pdf_file_path)
        pdf_text = ""
        for page_num in range(doc.page_count):
            page = doc.load_page(page_num)
            pdf_text += page.get_text("text")
        doc.close()
        return pdf_text
    except Exception as e:
        return f"Error extracting text: {e}"


# Extract the PDF text (can directly call this function in your script)
pdf_path = "the-spoon.pdf"
extracted_text = extract_text_from_pdf(pdf_path)

# Save the extracted text to a file (optional)
with open("pdf_text.txt", "w", encoding='utf-8') as file:
    file.write(extracted_text)

# Load the extracted PDF text (handling file errors)
try:
    with open('pdf_text.txt', 'r', encoding='utf-8') as file:
        pdf_text = file.read()
except FileNotFoundError:
    print("The extracted PDF text file 'pdf_text.txt' was not found.")
    exit(1)
except UnicodeDecodeError:
    print("Could not decode 'pdf_text.txt'. Please ensure it is encoded in UTF-8.")
    exit(1)

# Limit the prompt length if it's too long
max_prompt_length = 3000  # Adjust this to fit within model limits
if len(pdf_text) > max_prompt_length:
    pdf_text = pdf_text[:max_prompt_length]
    print("Warning: The extracted PDF text was too long and has been trimmed.")

# Define the PDF assistant template
pdf_assistant_template = pdf_text + """
You are an assistant that provides information based on the content of the PDF document.
Your role is to answer questions by referencing the content of the document. If the question is unrelated or the answer isn't in the document, respond with, "I can't assist you with that, sorry!" 
Question: {question} 
Answer: 
"""

# Create the prompt template for LLM
pdf_assistant_prompt_template = PromptTemplate(
    input_variables=["question"],
    template=pdf_assistant_template
)

# Use ChatOpenAI (adjust model as needed)
llm = ChatOpenAI(model='gpt-4', temperature=0, max_tokens=256)

# Create the LLM chain
llm_chain = pdf_assistant_prompt_template | llm


# Define the query function
def query_llm(question):
    try:
        # Get the response from LLM chain
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
    return render_template("index-pdf.html")


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
