import fitz  # PyMuPDF
from flask import Flask, render_template, request, jsonify
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
import tempfile


# Function to extract text from the PDF 
def extract_text_from_pdf(pdf_file):
    try:
        doc = fitz.open(pdf_file)
        pdf_text = ""
        for page_num in range(doc.page_count):
            page = doc.load_page(page_num)
            pdf_text += page.get_text("text")
        doc.close()
        return pdf_text
    except Exception as e:
        return f"Error extracting text: {e}"


# Initialize Flask app
app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index-pdf.html")


@app.route("/chatbot", methods=["POST"])
def chatbot():
    # Get the question from the frontend
    data = request.form
    question = data.get("question", "")
    
    # Get the uploaded PDF file
    pdf_file = request.files.get("pdf")
    if not pdf_file:
        return jsonify({"response": "No PDF file uploaded."})

    # Extract text from the uploaded PDF
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        pdf_file.save(temp_file)
        extracted_text = extract_text_from_pdf(temp_file.name)

    # Limit the prompt length if it's too long
    max_prompt_length = 3000  # Adjust this to fit within model limits
    if len(extracted_text) > max_prompt_length:
        extracted_text = extracted_text[:max_prompt_length]

    # Define the PDF assistant template
    pdf_assistant_template = extracted_text + """
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

    # Query the LLM
    try:
        response = llm_chain.invoke({'question': question})
        bot_response = response['content'] if isinstance(response, dict) else response.content
    except Exception as e:
        bot_response = "There was an error processing your request."

    return jsonify({"response": bot_response})


if __name__ == "__main__":
    app.run(debug=True)
