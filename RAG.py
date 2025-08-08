from langchain_ollama import OllamaLLM
from langchain.chains import RetrievalQA
from langchain_community.vectorstores import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain_community.document_loaders import UnstructuredHTMLLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader
import os


DIRECTORY = "rag_sources"
EMBEDDING_MODEL = "nomic-embed-text:v1.5"
LLM_MODEL = "gemma3:12b"


class RAG:
    def __init__(
        self,
        chunk_size=500,
        chunk_overlap=100,
        persist_directory="./chroma_db",
        embedding_model=EMBEDDING_MODEL,
        llm_model=LLM_MODEL,
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.persist_directory = persist_directory
        self.embedding_model = embedding_model
        self.llm_model = llm_model

        # Initialize the RAG system
        print("* Setting up RAG system...")
        self.documents = self.load_and_split_documents()
        self.vectordb = self.create_vector_store()
        self.retriever = self.vectordb.as_retriever()
        self.qa_chain = self.create_qa_chain()
        print("* RAG system setup complete.")

    def load_and_split_documents(self):
        """
        Load documents from the specified directory and split them into chunks.
        """
        datasources = []

        # Load documents from the specified directory
        for source in os.listdir(DIRECTORY):
            # HTML files
            if source.endswith(".html"):
                loader = UnstructuredHTMLLoader(os.path.join(DIRECTORY, source))

            # JSON or JSON-LD files
            elif source.endswith(".jsonld") or source.endswith(".json"):
                loader = TextLoader(os.path.join(DIRECTORY, source), encoding="utf-8")

            # Load the content
            loaded_data = loader.load()

            # Extend the datasources list with the loaded data
            datasources.extend(loaded_data)
            print(f" - Loaded {len(loaded_data)} documents from {source}")

        # Split documents
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
            add_start_index=True,
        )
        return text_splitter.split_documents(datasources)

    def create_vector_store(self):
        """
        Create a vector store from the loaded documents.
        """
        # Initialize embeddings
        print(" - Creating vector store...")
        embeddings = OllamaEmbeddings(model=self.embedding_model)

        # Create the vector store using Chroma
        vectordb = Chroma.from_documents(
            self.documents,
            embedding=embeddings,
            persist_directory=self.persist_directory,
        )
        return vectordb

    def create_qa_chain(self):
        """
        Create a question-answering chain using the retriever and the language model.
        """
        # Initialize the language model with reduced temperature for deterministic output
        llm = OllamaLLM(model=self.llm_model, temperature=0)

        # Create the RetrievalQA chain
        return RetrievalQA.from_chain_type(
            llm=llm, retriever=self.retriever, return_source_documents=True
        )

    def ask(self, query):
        """
        Ask a question and return the result along with the source documents.
        """
        # Invoke the QA chain with the query
        return self.qa_chain.invoke({"query": query})
