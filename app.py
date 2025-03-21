from flask import Flask, render_template, jsonify, request, session
from src.helper import download_hugging_face_embeddings
from langchain_pinecone import PineconeVectorStore
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
app.config['SESSION_PERMANENT'] = False  # Ensure session resets properly

# Load API keys
PINECONE_API_KEY = os.environ.get('PINECONE_API_KEY')
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')

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

# Initialize custom conversation memory using session
def get_conversation_memory():
    if 'chat_history' not in session:
        session['chat_history'] = []  # Store messages as a list
    return session['chat_history']

# Function to add messages to session memory
def add_to_conversation(role, message):
    if 'chat_history' not in session:
        session['chat_history'] = []
    
    session['chat_history'].append({"role": role, "message": message})
    session.modified = True  # Ensure session updates

# Collect and store patient details
def collect_patient_info(input):
    if 'patient_info' not in session:
        session['patient_info'] = {}
        session.modified = True
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

    # Collect patient info first
    patient_info_response = collect_patient_info(input)
    if patient_info_response:
        return patient_info_response

    patient_info = session.get('patient_info', {})
    memory = get_conversation_memory()  # Get stored chat history

    try:
        # Retrieve relevant documents from Pinecone
        retrieved_docs = retriever.invoke(input)
        retrieved_context = "\n".join([doc.page_content for doc in retrieved_docs]) if retrieved_docs else ""

        # If no relevant info found in Pinecone, respond with "I don't know, sorry."
        if not retrieved_context:
            return "I don't know, sorry."

        # Format conversation history
        conversation_history = "\n".join([f"{msg['role']}: {msg['message']}" for msg in memory])

        # Generate prompt for Gemini
        prompt_text = (
            f"You are a medical AI assistant. Use the retrieved context below to answer concisely."
            f"\n\nPatient Information:\n"
            f"Name: {patient_info.get('name', 'Unknown')}, "
            f"Age: {patient_info.get('age', 'Unknown')}, "
            f"Weight: {patient_info.get('weight', 'Unknown')} kg, "
            f"Height: {patient_info.get('height', 'Unknown')} cm, "
            f"Blood Group: {patient_info.get('blood_group', 'Unknown')}"
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

        # Add conversation to memory
        add_to_conversation("user", input)
        add_to_conversation("bot", generated_answer)

        return str(generated_answer)

    except Exception as e:
        print(f"Error retrieving documents: {e}")
        return "I'm currently unable to process your request. Please try again later."

@app.route("/reset", methods=["POST"])
def reset_session():
    session.clear()
    return jsonify({"message": "Chat session ended. All data cleared!"})

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080)