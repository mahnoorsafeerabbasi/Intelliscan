import google.generativeai as genai

gemini_key = "AIzaSyC7aHCqal7gJEDItUaQi-WMv-J4Z2uUA7Q"  # Replace with your Gemini API key
genai.configure(api_key=gemini_key)
model = genai.GenerativeModel('gemini-1.5-flash')

async def check_query_relevance_with_gemini(query: str):
    prompt = f"Determine if the following search query is relevant to computer science, programming, or technology: '{query}'. Please respond with 'yes' or 'no'."
    try:
        response = model.generate_content(prompt)
        response_text = response.text.strip().lower()
        print(f"Prompt: {prompt}")
        print(f"Response: {response_text}")
        return "yes" in response_text
    except Exception as e:
        print(f"Error: {e}")
        return False
