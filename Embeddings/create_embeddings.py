import os
import shutil
import openai
import re
from dotenv import load_dotenv
from langchain.schema import Document
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.document_loaders import TextLoader
from langchain.text_splitter import MarkdownHeaderTextSplitter

# Load environment variables
load_dotenv('environment.env')

# Set OpenAI API key
openai.api_key = os.getenv('OPENAI_API_KEY')

# Define paths
FAISS_INDEX_PATH = os.path.join("BackEnd", "Knowledge", "faiss_index")
FILE_PATH = os.path.join("BackEnd", "Embeddings", "info.md")


def main():
    """Main function to generate the FAISS database."""
    generate_data_store()


def generate_data_store():
    """Orchestrates the loading, splitting, and saving of the document."""
    documents = load_document()
    chunks = split_text(documents)
    save_to_faiss(chunks)


def load_document() -> list[Document]:
    """
    Loads a single Markdown document.

    Returns:
        List[Document]: A list containing the loaded document.
    """
    loader = TextLoader(FILE_PATH, encoding='utf-8')
    documents = loader.load()
    print(f"Loaded {len(documents)} document(s) from {FILE_PATH}.")
    return documents


def split_text(documents: list[Document]) -> list[Document]:
    """
    Splits the document into sections based on markdown headers.

    Args:
        documents (list[Document]): The list of loaded documents.

    Returns:
        list[Document]: A list of structured text chunks.
    """
    # Define markdown headers to use for chunking (H1 to H3)
    headers_to_split_on = [("#", "Title"), ("##", "Subtitle"), ("###", "Subsection")]

    text_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)

    chunks = []
    for doc in documents:
        chunks.extend(text_splitter.split_text(doc.page_content))

    print(f"Split {len(documents)} document(s) into {len(chunks)} chunk(s).")

    # Optional: Print a sample chunk for verification
    if chunks:
        sample_index = min(5, len(chunks) - 1)
        sample_doc = chunks[sample_index]
        print(f"\nSample Chunk #{sample_index + 1}:\n{sample_doc.page_content}\nMetadata: {sample_doc.metadata}\n")

    return chunks


def save_to_faiss(chunks: list[Document]):
    """
    Saves the text chunks to a FAISS vector database.

    Args:
        chunks (list[Document]): The list of text chunks to be saved.
    """
    # Remove existing FAISS index if it exists
    if os.path.exists(FAISS_INDEX_PATH):
        shutil.rmtree(FAISS_INDEX_PATH)
        print(f"Existing FAISS index at {FAISS_INDEX_PATH} has been removed.")

    # Initialize embeddings
    embeddings = OpenAIEmbeddings()

    # Create a new FAISS index from the documents
    db = FAISS.from_documents(
        documents=chunks,
        embedding=embeddings
    )

    # Persist the FAISS index to disk
    db.save_local(FAISS_INDEX_PATH)
    print(f"Saved {len(chunks)} chunk(s) to FAISS index at {FAISS_INDEX_PATH}.")


if __name__ == "__main__":
    main()
