import os
import streamlit as st
from langchain_community.document_loaders import PDFPlumberLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_ollama import OllamaEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama.llms import OllamaLLM


pdfs_directory = 'chat-with-pdf/pdfs/'
#let's be sure that the directory exists
os.makedirs(pdfs_directory, exist_ok=True)


template = """
You are an assistant for question-answering tasks. Use the following pieces of retrieved context to answer the question. If you don't know the answer, just say that you don't know. Use three sentences maximum and keep the answer concise.
Question: {question} 
Context: {context} 
Answer:
"""


embeddings = OllamaEmbeddings(model="deepseek-r1:14b")
model = OllamaLLM(model="deepseek-r1:14b")


if 'vector_store' not in st.session_state:
    st.session_state.vector_store = InMemoryVectorStore(embeddings)
if 'documents' not in st.session_state:
    st.session_state.documents = []


def save_pdf(file):
    file_path = os.path.join(pdfs_directory, file.name)
    with open(file_path, "wb") as f:
        f.write(file.getbuffer())
    return file_path

@st.cache_data(show_spinner=False)
def load_pdf(file_path):
    loader = PDFPlumberLoader(file_path)
    documents = loader.load()
    return documents

@st.cache_data
def split_text(_documents, chunk_size=1000, chunk_overlap=200, add_start_index=True):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        add_start_index=add_start_index
    )
    return text_splitter.split_documents(_documents)


def index_documents(documents):
    st.session_state.vector_store.add_documents(documents)

def retrieve_documents(query):
    return st.session_state.vector_store.similarity_search(query)

def answer_question(question, documents):
    context = "\n\n".join([doc.page_content for doc in documents])
    prompt = ChatPromptTemplate.from_template(template)
    chain = prompt | model
    return chain.invoke({"question": question, "context": context})


st.title("Chat with PDF Documents")

uploaded_files = st.file_uploader("Upload PDF(s)", type="pdf", accept_multiple_files=True)

if uploaded_files:
    for file in uploaded_files:
        with st.spinner(f"Processing {file.name}..."):
            file_path = save_pdf(file)
            try:
                docs = load_pdf(file_path)
                chunked_docs = split_text(docs)
                st.session_state.documents.extend(chunked_docs)
                index_documents(chunked_docs)
                st.success(f"{file.name} processed successfully.")
            except Exception as e:
                st.error(f"Error processing {file.name}: {str(e)}")

if st.button("Clear Uploaded Documents"):
    st.session_state.vector_store = InMemoryVectorStore(embeddings)
    st.session_state.documents = []
    st.success("Cleared all uploaded documents.")


question = st.chat_input("Ask a question about the PDFs:")

if question:
    st.chat_message("user").write(question)
    with st.spinner("Retrieving context and generating answer..."):
        related_docs = retrieve_documents(question)
        if related_docs:
            answer = answer_question(question, related_docs)
            st.chat_message("assistant").write(answer)
        else:
            st.chat_message("assistant").write("No relevant context found. Please try asking a different question.")
