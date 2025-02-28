# IntelliBot: RAG-based FAQ Bot for IntelliScan

## Overview

**IntelliBot** is a **Retriever-Augmented Generation (RAG)**-based FAQ bot designed specifically to answer questions related to the **IntelliScan** website. IntelliBot leverages advanced language models and AI to generate relevant answers based on the content of IntelliScan, ensuring that users receive precise and contextually accurate responses. The bot uses **Google's Gemini model** for embeddings and **Pinecone** for efficient vector storage and retrieval of data.

This bot is intended to improve user experience by providing quick and accurate answers to frequently asked questions (FAQs) related to IntelliScan, an AI-based platform used for code detection, plagiarism detection, and more. 

---

## Key Features:
- **FAQ-based Answering**: Designed to answer FAQs specifically related to **IntelliScan**.
- **Retriever-Augmented Generation (RAG)**: Combines both **retrieval-based** and **generation-based** approaches to produce more accurate answers.
- **Gemini API Integration**: Utilizes Google's **Gemini model** for generating embeddings of queries and documents.
- **Pinecone Vector Database**: Uses **Pinecone** to store and retrieve document embeddings, providing a fast and efficient way to answer user queries.
- **Contextual Accuracy**: Provides highly relevant answers to questions by analyzing stored embeddings and generating responses that directly reference IntelliScan.

---

## Why IntelliBot?

The IntelliBot was built with the goal of improving user interaction and support for **IntelliScan** users by automating the FAQ process. Instead of users needing to navigate the website to find answers, IntelliBot serves as an intelligent assistant capable of answering any questions directly related to the platform. By leveraging **RAG** techniques and AI-powered embeddings, the bot can generate responses that feel natural and contextually appropriate.

With its use of **Pinecone**, it ensures that responses are fast, accurate, and come from a reliable source of truth, making it an invaluable tool for IntelliScan users.

---

## Technologies Used

- **FastAPI**: A modern web framework for building APIs with Python.
- **Google Gemini API**: For generating high-quality embeddings and responding to queries.
- **Pinecone**: A vector database used to store and search document embeddings.
- **Python 3.x**: The core programming language used to build IntelliBot.
- **Pydantic & Uvicorn**: Used for data validation and serving the API.

---

## Setup and Installation

### Prerequisites

- **Python 3.x** (preferably 3.7+)
- **Google Gemini API Key**: Obtain your API key from [Google Cloud Console](https://console.cloud.google.com/).
- **Pinecone API Key**: Obtain your API key from [Pinecone](https://www.pinecone.io/).
- **IntelliScan Knowledge Base**: A repository of documents or FAQ data related to IntelliScan that the bot can use to answer questions.
