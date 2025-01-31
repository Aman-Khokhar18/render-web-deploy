import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_community.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
import logging
import atexit

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
FAISS_INDEX_PATH = os.path.join("BackEnd", "Knowledge", "faiss_index")
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

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
if not OPENAI_API_KEY:
    logger.error("OpenAI API key not found in environment variables.")
    raise ValueError("OpenAI API key not found in environment variables.")

app = Flask(__name__)
CORS(app)

def load_vector_store():
    """Loads the FAISS vector store with OpenAI embeddings."""
    try:
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

# Load the vector store once at startup
try:
    vector_store = load_vector_store()
except Exception as e:
    logger.critical("Application cannot start without a loaded vector store.")
    exit(1)

def query_faiss(query_text, history=None, k=8, relevance_threshold=0.6):
    """
    Queries the FAISS vector store and returns a response.

    :param query_text: The user's question
    :param history: Optional conversation history
    :param k: Number of top similar results to fetch
    :param relevance_threshold: Minimum score to consider a result valid
    :return: AI-generated response
    """
    try:
        logger.info(f"Received query: '{query_text}' with history: '{history}'")
        results = vector_store.similarity_search_with_relevance_scores(query_text, k=k)
        logger.info(f"Similarity search completed. Retrieved {len(results)} results.")

        # Log relevance scores
        for idx, (doc, score) in enumerate(results, start=1):
            logger.debug(f"Result {idx}: Score = {score:.4f}, Source = {doc.metadata.get('source', 'Unknown')}")

        # Filter out documents below the threshold
        relevant_results = [(doc, score) for doc, score in results if score >= relevance_threshold]
        logger.info(f"Filtered down to {len(relevant_results)} relevant results using threshold {relevance_threshold}.")

        if relevant_results:
            # Merge top results into context
            context_text = "\n\n---\n\n".join([doc.page_content[:800] for doc, _ in relevant_results])
            logger.debug(f"Constructed context with {len(relevant_results)} documents.")
        elif results:
            # If no documents pass the threshold, but some results exist, use the most relevant one
            best_match = results[0][0].page_content[:800]
            context_text = f"(Closest available information found, but relevance is low)\n\n{best_match}"
            logger.warning("No highly relevant results found, using best available match.")
        else:
            context_text = ""

        history_str = history if history else "No history available."
        formatted_history = f"User: {history_str}\n"

        # Build prompt
        prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE_WITH_CONTEXT)
        prompt = prompt_template.format(
            context=context_text,
            history=formatted_history,
            question=query_text
        )
        logger.info("Constructed prompt with available context.")

        # Initialize ChatOpenAI model
        model = ChatOpenAI(openai_api_key=OPENAI_API_KEY, temperature=0.5)
        response_text = model.predict(prompt)

        logger.info("AI response generated successfully.")
        return response_text

    except Exception as e:
        logger.error(f"Error during query_faiss: {e}")
        raise

# Register shutdown function
def shutdown():
    logger.info("Shutdown initiated. FAISS does not require persistence.")

atexit.register(shutdown)

@app.route("/chat", methods=["POST"])
def chat_endpoint():
    """
    Expects JSON body with:
      {
        "message": "User's question",
        "history": "Optional conversation history"
      }
    Returns:
      {
        "reply": "AI's response"
      }
    """
    data = request.get_json()
    user_message = data.get("message", "").strip()
    conversation_history = data.get("history", "").strip()

    if not user_message:
        logger.warning("No user message provided in the request.")
        return jsonify({"error": "No user message provided"}), 400

    try:
        response = query_faiss(user_message, history=conversation_history, k=8, relevance_threshold=0.6)
        return jsonify({"reply": response})
    except Exception as e:
        logger.error(f"Error in /chat endpoint: {e}")
        return jsonify({"error": "Something went wrong"}), 500

if __name__ == "__main__":
    app.run()
