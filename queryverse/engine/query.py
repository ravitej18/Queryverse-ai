from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings

def get_retrieval_chain(vector_store):
    """
    Creates and returns a modern retrieval chain using LCEL.
    """
    model = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.3)
    
    retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 3})

    prompt_template = """
    Answer the question as detailed as possible from the provided context. Make sure to provide all the details. If the answer is not in
    the provided context, just say, "The answer is not available in the context." Do not provide a wrong answer.\n\n
    Context:\n {context}?\n
    Question: \n{question}\n

    Answer:
    """
    prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])

    # This is the modern LCEL (LangChain Expression Language) way to build chains
    chain = (
        {"context": retriever, "question": RunnablePassthrough()}
        | prompt
        | model
        | StrOutputParser()
    )
    
    return chain

def user_input(user_question: str):
    """
    Handles user input by querying the vector store and generating a response.
    
    Args:
        user_question (str): The user's question.

    Returns:
        dict: A dictionary containing the answer.
    """
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    
    # allow_dangerous_deserialization is needed for FAISS with langchain
    vector_store = FAISS.load_local("vector_store", embeddings, allow_dangerous_deserialization=True)
    
    chain = get_retrieval_chain(vector_store)
    
    # Use .invoke() which is the new standard method
    response = chain.invoke(user_question)
    
    return {"answer": response}

