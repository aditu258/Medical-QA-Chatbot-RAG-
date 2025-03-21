from flask import Flask, render_template, jsonify, request, session
from src.helper import download_hugging_face_embeddings
from langchain_pinecone import PineconeVectorStore
from langchain.memory import ConversationBufferMemory
from dotenv import load_dotenv
import os
import google.generativeai as genai
from pinecone import Pinecone
from google.api_core.exceptions import ResourceExhausted

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'supersecretkey')

# Load API keys
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

# Initialize conversation memory
def get_conversation_memory():
    if 'memory' not in session:
        session['memory'] = []
    return ConversationBufferMemory(memory_key="history", return_messages=True)

def add_to_conversation(memory, role, message):
    if role == "user":
        memory.chat_memory.add_user_message(message)
    elif role == "bot":
        memory.chat_memory.add_ai_message(message)

def save_conversation_history(memory):
    session['memory'] = [
        {"role": "user", "message": msg.content} if msg.type == "human" else {"role": "bot", "message": msg.content}
        for msg in memory.chat_memory.messages
    ]
    session.modified = True

# Collect and store patient details
def collect_patient_info(input):
    if 'patient_info' not in session:
        session['patient_info'] = {}
        return "Hello! I am AI Doctor. Let's start with some basic details.\nWhat is your full name?"

    patient_info = session['patient_info']

    if 'name' not in patient_info:
        patient_info['name'] = input
        session.modified = True
        return "Got it! Please enter your age (e.g., 25)."
    elif 'age' not in patient_info:
        try:
            patient_info['age'] = int(input)
            session.modified = True
            return "Now, enter your weight in kg (e.g., 70)."
        except ValueError:
            return "Please enter a valid age."
    elif 'weight' not in patient_info:
        patient_info['weight'] = input
        session.modified = True
        return "Next, enter your height in cm (e.g., 170)."
    elif 'height' not in patient_info:
        patient_info['height'] = input
        session.modified = True
        return "Lastly, what is your blood group? (e.g., O+, A-)"
    elif 'blood_group' not in patient_info:
        patient_info['blood_group'] = input
        session.modified = True
        return f"Thanks, {patient_info['name']}! Now, how can I help you with your medical concerns?"
    return None  # All details are collected

# Define routes

@app.route("/")
def index():
    return render_template('chat.html')

@app.route("/get", methods=["GET", "POST"])
def chat():
    msg = request.form["msg"]
    input = msg.strip()

    # Initialize memory
    memory = get_conversation_memory()

    # Collect patient info first
    patient_info_response = collect_patient_info(input)
    if patient_info_response:
        return patient_info_response

    patient_info = session['patient_info']

    try:
        # Retrieve relevant documents from Pinecone
        retrieved_docs = retriever.invoke(input)
        retrieved_context = "\n".join([doc.page_content for doc in retrieved_docs]) if retrieved_docs else ""

        # If no relevant info found in Pinecone, respond with "I don't know, sorry."
        if not retrieved_context:
            return "I don't know, sorry."

        # Add user input to memory
        add_to_conversation(memory, "user", input)

        # Generate prompt for Gemini
        conversation_history = memory.load_memory_variables({})['history']
        prompt_text = (
            f"You are a medical AI assistant. Use the retrieved context below to answer concisely."
            f"\n\nPatient Information:\nName: {patient_info['name']}, Age: {patient_info['age']}, Weight: {patient_info['weight']} kg, Height: {patient_info['height']} cm, Blood Group: {patient_info['blood_group']}"
            f"\n\nContext:\n{retrieved_context}"
            f"\n\nConversation History:\n{conversation_history}"
            f"\n\nQuestion: {input}"
            f"\nAnswer in 2-3 sentences:"
        )

        # Generate response using Gemini
        try:
            response = gemini_model.generate_content(prompt_text)
            generated_answer = response.text.strip() if response.text else "I'm sorry, I can't answer that."
        except ResourceExhausted:
            generated_answer = "I'm currently unable to process your request due to high demand. Please try again later."
        except Exception as e:
            print(f"Error generating response: {e}")
            generated_answer = "An error occurred while processing your request. Please try again."

        # Add bot response to memory
        add_to_conversation(memory, "bot", generated_answer)
        save_conversation_history(memory)
        return str(generated_answer)

    except Exception as e:
        print(f"Error retrieving documents: {e}")
        return "I'm currently unable to process your request. Please try again later."

@app.route("/reset", methods=["POST"])
def reset_session():
    session.clear()
    return jsonify({"message": "Chat session ended. All data cleared!"})

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080, debug=True)
