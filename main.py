from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from vector import retriever
from sentiment import analyze_sentiment


model = OllamaLLM(model="mistral")

template = """
You are an expert in answering questions about a pizza restaurant

Here are some relevant reviews: {reviews}

Here is the question to answer: {question}
"""
prompt = ChatPromptTemplate.from_template(template)
chain = prompt | model

while True:
    print("\n\n-------------------------------")
    question = input("Ask your question (q to quit): ")
    print("\n\n")
    if question == "q":
        break

    # Step 1: Get top 5 relevant reviews
    reviews = retriever.invoke(question)

    # Step 2: Analyze sentiment for each review
    print("Sentiment Analysis of Relevant Reviews:\n")
    for i, review in enumerate(reviews):
        text = review.page_content
        sentiment = analyze_sentiment(text)
        print(f"Review {i+1}: {sentiment['label']} - {text[:80]}...")
    
    # Step 3: Run through RAG LLM pipeline
    result = chain.invoke({
        "reviews": "\n\n".join([doc.page_content for doc in reviews]),
        "question": question
    })
    print("\nLLM Answer:\n", result)
