from flask import Flask, render_template, jsonify, request
from src.helper import download_hugging_face_embeddings
from langchain_pinecone import PineconeVectorStore
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
from src.prompt import *
import os
import google.generativeai as genai
from pinecone import Pinecone

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Load environment variables
PINECONE_API_KEY = os.environ.get('PINECONE_API_KEY')
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')

os.environ["PINECONE_API_KEY"] = PINECONE_API_KEY
os.environ["GEMINI_API_KEY"] = GEMINI_API_KEY

# Initialize Pinecone
pc = Pinecone(api_key=PINECONE_API_KEY)
index_name = "test"

# Check if Pinecone index exists
try:
    indexes = pc.list_indexes()
    print("Pinecone connection successful. Available indexes:", indexes)
    if index_name not in indexes.names():
        print(f"Index '{index_name}' does not exist in Pinecone.")
    else:
        print(f"Index '{index_name}' exists.")
except Exception as e:
    print("Failed to connect to Pinecone:", e)

# Initialize embeddings
embeddings = download_hugging_face_embeddings()

# Connect to Pinecone index
docsearch = PineconeVectorStore.from_existing_index(
    index_name=index_name,
    embedding=embeddings
)

# Create retriever
retriever = docsearch.as_retriever(search_type="similarity", search_kwargs={"k": 3})

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)
gemini_model = genai.GenerativeModel("models/gemini-1.5-pro-latest")

# Define prompt template
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        ("human", "{input}"),
    ]
)

# Define routes
@app.route("/")
def index():
    return render_template('chat.html')

@app.route("/get", methods=["GET", "POST"])
def chat():
    msg = request.form["msg"]
    input = msg
    print("User Input:", input)

    # Retrieve relevant documents
    retrieved_docs = retriever.invoke(input)
    print("Retrieved Documents:", retrieved_docs)

    if not retrieved_docs:
        retrieved_context = "No relevant information found."
    else:
        retrieved_context = "\n".join([doc.page_content for doc in retrieved_docs])

    # Generate prompt for Gemini
    prompt_text = (
        f"You are a medical AI assistant. Use the retrieved context below to answer the question concisely."
        f"\n\nContext:\n{retrieved_context}"
        f"\n\nQuestion: {input}"
        f"\nAnswer in 2-3 sentences:"
    )

    # Generate response using Gemini
    response = gemini_model.generate_content(prompt_text)
    generated_answer = response.text.strip() if response.text else "I'm sorry, I can't answer that."

    print("Response:", generated_answer)
    return str(generated_answer)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080, debug=True)