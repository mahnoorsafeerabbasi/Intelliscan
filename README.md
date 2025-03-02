# Intelliscan Source Code Search

Intelliscan is an advanced AI-powered source code search and plagiarism detection platform. It allows users to search, analyze, and detect AI-generated vs. human-written code, check for code vulnerabilities, and perform other security-related tasks. 

## Features
- **AI Code Plagiarism Checker**: Detects AI-generated vs. human-written code.
- **Class Assignments Plagiarism Checker**: Compares student submissions to find similarities.
- **FAQ Chatbot**: Provides instant answers related to Intelliscan features.
- **Code Security Checker**: Detects vulnerabilities and potential threats in source code.
- **Multi-Language Support**: Works with Python, Java, C++, JavaScript, and more.
- **Integrated Search**: Fetches relevant source code from GitHub and Google Custom Search API.

## Installation & Setup
### Prerequisites
Ensure you have the following installed:
- **Node.js** (for Next.js frontend)
- **Python** (for FastAPI backend)
- **Docker** (if running Dolos or other integrated tools)
- **Git** (for version control)


### Backend Setup (FastAPI)
1. Navigate to the backend directory:
   ```sh
   cd serverside
   ```
2. Create and activate a virtual environment:
   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
4. Run the FastAPI server:
   ```sh
   uvicorn app.main:app --reload
   ```

### Frontend Setup (Next.js)
1. Navigate to the frontend directory:
   ```sh
   cd clientside
   ```
2. Install dependencies:
   ```sh
   npm install
   ```
3. Start the development server:
   ```sh
   npm run dev
   ```
4. Open [http://localhost:3000](http://localhost:3000) in your browser.

## API Integration
Intelliscan integrates GitHub API and Google Custom Search API for fetching relevant source code. Ensure you set up your API keys in a `.env` file:
```env
GITHUB_PAT=your_github_personal_access_token
GOOGLE_API_KEY=your_google_custom_search_api_key
GOOGLE_CX=your_google_custom_search_engine_id
```
