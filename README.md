# ReviewIQ: AI-Powered Customer Feedback Analyzer

**ReviewIQ** is a local LLM-powered web app that analyzes customer reviews from CSV files and generates structured summaries, insights, and business recommendations. It uses **LangChain**, **Ollama**, and **Chroma vector search** in a **RAG (Retrieval-Augmented Generation)** pipeline, making it a powerful tool for understanding customer sentiment, service quality, and actionable improvements.

---

## Features

-  **Upload CSV reviews** (e.g., from a restaurant)
-  **Ask questions** like:
  - "How is the ambience of the restaurant?"
  - "What do people say about the service?"
-  **Aspect-based sentiment analysis** (Food, Ambience, Service, Price)
-  **Interactive ChatBot UI
-  **Interactive dashboards** with sentiment trends and word clouds
-  **Multilingual support** for reviews
-  **Local LLMs (e.g., Mistral)** with Ollama – **runs offline**
  
## Future enhancements-
  
-  **Live web scraping** (Zomato/Yelp support planned)
-  **Generate smart suggestions** to improve the business
-  User portal (coming soon): Upload datasets, save insights, generate reports

---

## 🧱 Tech Stack

| Component           | Technology Used           |
|---------------------|---------------------------|
| LLM                 | [Ollama](https://ollama.com/) (e.g., `mistral`, `llama3`) |
| Chain Orchestration| [LangChain](https://www.langchain.com/) |
| Embeddings & Search| Chroma + Ollama Embeddings |
| Dashboard           | Plotly, Matplotlib        |
| CSV Parsing         | Pandas, LangChain CSVLoader |
| PDF Reporting       | reportlab / pdfkit        |


