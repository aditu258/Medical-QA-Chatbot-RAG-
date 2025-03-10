# MediBot - Medical AI Chatbot

MediBot is a **Medical AI Chatbot** designed to assist users with medical queries by utilizing **Pinecone**, **LangChain**, and **Gemini AI** for document search and response generation. The chatbot efficiently retrieves medical data from uploaded PDFs and provides concise answers based on the extracted knowledge base.

## Features

✅ PDF document loading and processing  
✅ Text chunking for efficient data handling  
✅ Hugging Face embeddings for semantic understanding  
✅ Pinecone vector search for fast and accurate retrieval  
✅ Gemini AI for generating precise medical responses  
✅ Flask API for interactive communication  

## Project Structure

```
📂 MediBot
 ┣ 📂 Data                 # PDF documents for knowledge base
 ┣ 📂 env-medibot          # Virtual environment folder
 ┣ 📂 research             # Contains trials.ipynb (Main implementation notebook)
    ┗ 📜 trials.ipynb      # Main code implementation in Jupyter Notebook
 ┣ 📜 .env                 # Environment variables (API keys)
 ┣ 📜 .gitignore           # Files to ignore in version control
 ┗ 📜 requirements.txt     # Project dependencies
```

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-repo/MediBot.git
   cd MediBot
   ```
2. Create and activate the virtual environment:
   ```bash
   conda create -n env-medibot python=3.12
   conda activate env-medibot
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Set up your `.env` file with the following keys:
   ```
   PINECONE_API_KEY=your_pinecone_api_key
   GEMINI_API_KEY=your_gemini_api_key
   ```

## Usage

1. Run the Jupyter Notebook:
   ```bash
   jupyter notebook
   ```
2. Open `trials.ipynb` inside the `research` folder and execute the cells to:
   - Load PDF documents
   - Split text into chunks
   - Create embeddings
   - Upsert vectors into Pinecone
   - Generate AI responses using Gemini

## API Endpoints

🚀 `/ask` - Accepts POST requests with JSON data:

```json
{
   "query": "What are the side effects of paracetamol?"
}
```

Response:

```json
{
   "prompt": "What are the side effects of paracetamol?",
   "retrieved_context": "...medical context...",
   "generated_answer": "Paracetamol overdose may cause liver damage..."
}
```

## Contributors

- **Aditya Sinha** - *ML Engineer*

## License

This project is licensed under the **MIT License**.

