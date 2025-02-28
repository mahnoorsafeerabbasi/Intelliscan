# IntelliLearn: A Platform for Students to Access GitHub Repos, Web Searches, and YouTube Videos

## Overview

**IntelliLearn** is an all-in-one platform designed to help students easily access relevant learning resources. By using GitHub's API, Google's Custom Search API, and YouTube's API, this platform provides students with relevant **GitHub repositories**, **web search results**, and **YouTube videos** — all in one place. What makes IntelliLearn unique is its ability to filter search results specifically for **Computer Science** topics using **Google's Gemini model**.

The primary goal of **IntelliLearn** is to provide a comprehensive learning experience for students, especially those new to programming and computer science. With IntelliLearn, students can access top-notch resources in one place, reducing the time and effort spent searching across multiple platforms.

### Key Features:
- **GitHub Repository Search**: Search and find GitHub repositories related to programming, algorithms, and other computer science topics.
- **Web Search**: Powered by Google Custom Search, it provides web results relevant to computer science concepts, tutorials, articles, and more.
- **YouTube Video Search**: Find educational YouTube videos that align with your specific computer science topics.
- **Gemini Model Filtering**: Uses **Google Gemini** to restrict search results specifically to **computer science** topics, ensuring that only relevant content is returned.

---

## Why IntelliLearn?

The idea behind IntelliLearn is to streamline the search process for students who are looking for relevant learning resources on **GitHub**, **YouTube**, and the **web**. Rather than searching these platforms separately, IntelliLearn integrates them all into one user-friendly interface and uses the Gemini model to ensure that results are tailored specifically to computer science topics.

By using APIs like **GitHub API**, **Google Custom Search API**, and **YouTube API**, IntelliLearn is able to provide valuable learning content for students. The Gemini model, which filters out irrelevant search results, helps improve the quality and relevance of content by targeting computer science-focused queries.

---

## Technologies Used

- **FastAPI**: Web framework for building the backend API.
- **Google Gemini**: To restrict search results to relevant computer science content.
- **GitHub API**: For searching relevant GitHub repositories.
- **Google Custom Search API**: To perform web searches tailored to computer science topics.
- **YouTube Data API**: To fetch relevant YouTube videos based on search queries.
- **Pydantic & Uvicorn**: For data validation and serving the API.
- **Python 3.x**: The primary language for building the platform.

---

## Setup and Installation

### Prerequisites

- **Python 3.x** (preferably 3.7+)
- **Google Custom Search API Key**: You can get your API key from [Google Cloud Console](https://console.cloud.google.com/).
- **YouTube Data API Key**: Get it from [Google Cloud Console](https://console.cloud.google.com/).
- **GitHub Access Token**: To authenticate and interact with GitHub API (optional but recommended).
- **Gemini Model Access**: You’ll need to configure access to Gemini for content filtering.

