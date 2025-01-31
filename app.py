import os
import logging
import atexit
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_community.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv('environment.env')

# Configuration
FAISS_INDEX_PATH = "faiss_index"
PROMPT_TEMPLATE_WITH_CONTEXT = """
<BEGIN CONVERSATION>

System:
You are a knowledgeable personal assistant for Aman Khokhar. You have access to his detailed resume and will answer questions based solely on this information. 
If exact information is not found, use the closest available details to make an informed response. Do not fabricate facts.
If no relevant details exist at all, state that you do not have the information.

Context:
{context}

{history}

User:
{question}

Assistant:
"""

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    logger.error("OpenAI API key not found in environment variables.")
    raise ValueError("OpenAI API key not found in environment variables.")

app = Flask(__name__)
CORS(app)

def load_vector_store():
    """Loads the FAISS vector store with OpenAI embeddings."""
    try:
        if not os.path.exists(FAISS_INDEX_PATH):
            raise FileNotFoundError(f"FAISS index directory '{FAISS_INDEX_PATH}' not found.")
        
        embedding_function = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
        db = FAISS.load_local(
            FAISS_INDEX_PATH,
            embeddings=embedding_function,
            allow_dangerous_deserialization=True
        )
        logger.info(f"FAISS vector store loaded from {FAISS_INDEX_PATH}.")
        return db
    except Exception as e:
        logger.error(f"Failed to load FAISS vector store: {e}")
        raise

# Load the vector store at startup
try:
    vector_store = load_vector_store()
except Exception as e:
    logger.critical("Application cannot start without a loaded vector store.")
    exit(1)

def query_faiss(query_text, history=None, k=8, relevance_threshold=0.6):
    """
    Queries the FAISS vector store and returns a response.
    """
    try:
        logger.info(f"Received query: '{query_text}' with history: '{history}'")
        results = vector_store.similarity_search_with_relevance_scores(query_text, k=k)
        logger.info(f"Retrieved {len(results)} results.")

        relevant_results = [(doc, score) for doc, score in results if score >= relevance_threshold]
        logger.info(f"Filtered down to {len(relevant_results)} relevant results using threshold {relevance_threshold}.")

        context_text = "\n\n---\n\n".join([doc.page_content[:800] for doc, _ in relevant_results]) if relevant_results else ""
        
        history_str = history if history else "No history available."
        formatted_history = f"User: {history_str}\n"

        prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE_WITH_CONTEXT)
        prompt = prompt_template.format(context=context_text, history=formatted_history, question=query_text)

        model = ChatOpenAI(openai_api_key=OPENAI_API_KEY, temperature=0.5)
        response_text = model.predict(prompt)

        return response_text

    except Exception as e:
        logger.error(f"Error during query_faiss: {e}")
        return "An error occurred while processing your request."

def shutdown():
    logger.info("Shutdown initiated. FAISS does not require persistence.")

atexit.register(shutdown)

@app.route("/chat", methods=["POST"])
def chat_endpoint():
    data = request.get_json()
    user_message = data.get("message", "").strip()
    conversation_history = data.get("history", "").strip()

    if not user_message:
        return jsonify({"error": "No user message provided"}), 400

    try:
        response = query_faiss(user_message, history=conversation_history, k=8, relevance_threshold=0.6)
        return jsonify({"reply": response})
    except Exception as e:
        logger.error(f"Error in /chat endpoint: {e}")
        return jsonify({"error": "Something went wrong"}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
