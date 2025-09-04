QueryVerse ✨
QueryVerse is a personal knowledge engine that allows you to "chat" with your documents. Upload a PDF or TXT file and ask questions to get context-aware answers powered by Google Gemini and LangChain.

Features
Stunning UI: A modern, dark-themed interface built with Streamlit.

Document Support: Upload and process .pdf and .txt files.

RAG Pipeline: Utilizes a Retrieval-Augmented Generation pipeline for accurate, context-based answers.

Powered by Gemini: Leverages Google's Gemini Pro for generation and state-of-the-art embedding models.

Setup & Installation
Clone the repository:

git clone <your-repo-url>
cd queryverse

Create a virtual environment and activate it:

python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`

Install the dependencies:

pip install -r requirements.txt

Set up your API Key:

Rename the .env.example file to .env.

Open the .env file and replace "YOUR_API_KEY_HERE" with your actual Google API Key.

How to Run
Make sure your virtual environment is activated.

Run the Streamlit application from your terminal:

streamlit run app.py

Your browser will open with the QueryVerse application ready to use.