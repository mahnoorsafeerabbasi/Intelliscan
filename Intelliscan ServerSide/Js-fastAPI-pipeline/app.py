from email.mime import text
import os
import re
from tkinter import font
from turtle import color
import torch
import matplotlib.pyplot as plt
from fastapi import FastAPI, APIRouter, HTTPException, UploadFile, File, Form, background
import numpy as np
import io
import base64
from fastapi import FastAPI, APIRouter, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse
from transformers import AutoTokenizer, AutoModel
from pinecone import Pinecone
import google.generativeai as genai
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from services import process_input  # Importing the process_input function
from fastapi.middleware.cors import CORSMiddleware
import base64
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, 
    Paragraph, 
    Spacer, 
    Image,
    ListFlowable,
    ListItem
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus.paragraph import Paragraph


# API Keys and configurations 
#AIzaSyCPW8EMFYkdTMyAk3gGZW76w4cWO5apXpU
API_KEY = "AIzaSyCPW8EMFYkdTMyAk3gGZW76w4cWO5apXpU"
PINECONE_API_KEY = "0a248db7-1c0a-46d8-999d-ac588e3419d5"
INDEX_NAME = "javascript-plagiarism-detection"
MODEL_NAME = 'bert-base-uncased'

# Initialize Pinecone
pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(INDEX_NAME)

# Initialize BERT model and tokenizer
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModel.from_pretrained(MODEL_NAME)

# Initialize Gemini model
genai.configure(api_key=API_KEY)
gemini_model = genai.GenerativeModel('gemini-1.5-flash') #gemini-1.5-pro-exp-0827

analysis_results = {}

# Function to preprocess code
def preprocess_code(code):
    code = re.sub(r'//.*?\n', '', code)  # Single line comments
    code = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)  # Multi-line comments
    code = re.sub(r'\s+', ' ', code)
    return code.strip()

# Function to convert code to vectors using BERT model
def convert_code_to_vectors(code_snippets):
    vectors = []
    for snippet in code_snippets:
        inputs = tokenizer(snippet, return_tensors="pt", padding=True, truncation=True, max_length=512)
        with torch.no_grad():
            outputs = model(**inputs)
        vector = outputs.last_hidden_state.mean(dim=1).detach().numpy().flatten()
        vectors.append(vector)
    return vectors

# Function to find the top N most similar vectors in Pinecone index
def find_top_matches(code, top_k=5):
    processed_code = preprocess_code(code)
    vector = convert_code_to_vectors([processed_code])[0]
    query_response = index.query(vector=vector.tolist(), top_k=top_k, include_metadata=True)
    matches = query_response.matches if query_response.matches else []
    return matches

# Function to get AI and human percentages from Gemini model
def get_gemini_percentages(code_snippet):
    analysis_prompt = (
        f"Evaluate the following code snippet and estimate the percentage of human-written code and AI-generated code. "
        f"Provide two percentage estimates (as numbers between 0 and 100) based on patterns such as complexity, verbosity, and lack of comments. "
        f"Your response should be in the format 'AI_percentage, Human_percentage':\n\n{preprocess_code(code_snippet)}"
    )
    
    response = gemini_model.generate_content(analysis_prompt).text.strip()
    percentages = re.findall(r"(\d+(\.\d+)?)", response)
    
    if len(percentages) >= 2:
        ai_percentage = float(percentages[0][0])
        human_percentage = float(percentages[1][0])
        return ai_percentage, human_percentage

    return 0.0, 0.0  # Default if not found

# Function to analyze code with Gemini model based on final verdict
def analyze_code_with_gemini(code_snippet, final_verdict):
    analysis_prompt = (
        f"Analyze the following code snippet with a final AI generation verdict of {final_verdict:.2f}%. "
        "Provide your response in the following structured format:\n\n"
        "## Overall Assessment\n"
        "Brief summary of AI vs. human-written code\n\n"
        "## Characteristics of AI-Generated Code\n"
        "- Bullet point 1\n"
        "- Bullet point 2\n\n"
        "## Characteristics of Human-Written Code\n"
        "- Bullet point 1\n"
        "- Bullet point 2\n\n"
        "## Detailed Analysis\n"
        "Paragraph explaining the reasoning behind the assessment.\n\n"
        f"Code Snippet:\n```\n{code_snippet}\n```"
    )
    
    response = gemini_model.generate_content(analysis_prompt).text.strip()
    return response
def format_gemini_response(gemini_response):
    # Replace markdown headers with HTML <h2>, <h3>, etc.
    gemini_response = re.sub(r'## (.*)', r'<h2 style="color:#007BFF;">\1</h2>', gemini_response)
    
    # Replace bold markdown syntax (**) with HTML <strong> for bold text
    gemini_response = re.sub(r'\*\*(.*?)\*\*', r'<strong style="color:#28a745;">\1</strong>', gemini_response)

    # Optionally, replace other markdown elements like bullet points or code formatting
    gemini_response = re.sub(r'- (.*)', r'<ul><li>\1</li></ul>', gemini_response)  # For bulleted lists

    # Add other custom HTML formatting as needed
    gemini_response = f'<div style="font-family: Arial, sans-serif; line-height: 1.6;">{gemini_response}</div>'
    
    return gemini_response

# Function to compute Pinecone-based percentages for AI and human
def calculate_pinecone_percentages(matches):
    total_matches = len(matches)
    if total_matches == 0:
        return 0.0, 0.0  # No matches found, assume 0% for both

    ai_count = sum(1 for match in matches if match.metadata.get("dataset_type") == "AI")
    human_count = sum(1 for match in matches if match.metadata.get("dataset_type") == "human")

    ai_percentage = (ai_count / total_matches) * 100
    human_percentage = (human_count / total_matches) * 100
    return ai_percentage, human_percentage

# Function to calculate final verdict
def calculate_final_verdict(gemini_percentage, pinecone_ai_percentage, pinecone_human_percentage):
    # Determine the final verdict based on the given conditions
    if pinecone_human_percentage > 50:
        return (gemini_percentage + pinecone_ai_percentage) / 2
    elif pinecone_ai_percentage >= 50:
        return pinecone_ai_percentage
    else:
        return pinecone_human_percentage

# Function to create visualizations
def create_visualizations(final_verdict):
    total_ai = final_verdict
    total_human = 100 - final_verdict

    total_ai = max(total_ai, 0)
    total_human = max(total_human, 0)

    labels = ['AI', 'Human']
    sizes = [total_ai, total_human]
    colors = ['gold', 'lightskyblue']
    
    plt.figure(figsize=(12, 6))
    
    plt.subplot(1, 2, 1)
    plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=140)
    plt.axis('equal')
    plt.title('AI vs Human Code Contribution Based on Final Verdict')

    plt.subplot(1, 2, 2)
    data = [1] * int(total_ai) + [0] * int(total_human)
    plt.hist(data, bins=[0, 1, 2], color='lightblue', edgecolor='black', alpha=0.7)
    plt.xticks([0, 1], ['Human', 'AI'])
    plt.xlabel('Code Type')
    plt.ylabel('Frequency')
    plt.title('Histogram of AI vs Human Code Based on Final Verdict')

    buf = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    return base64.b64encode(buf.getvalue()).decode('utf-8')

# Function to generate PDF report
def generate_pdf_report(file_name, code, reasoning, final_verdict, pie_histogram_base64):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle', 
        parent=styles['Title'], 
        fontSize=16, 
        textColor=colors.darkblue,
        spaceAfter=12
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle', 
        parent=styles['Heading2'], 
        fontSize=14, 
        textColor=colors.darkgreen,
        spaceAfter=6
    )
    
    code_style = ParagraphStyle(
        'CodeStyle', 
        parent=styles['Normal'], 
        fontName='Courier',
        fontSize=10,
        backColor=colors.lightgrey,
        borderPadding=6,
        borderColor=colors.grey,
        borderWidth=1,
        spaceAfter=12
    )

    story = []

    # Title
    story.append(Paragraph("IntelliScan: AI Code Detection Report", title_style))
    story.append(Spacer(1, 12))
    
    # File Details
    story.append(Paragraph(f"File Analyzed: {file_name}", subtitle_style))
    
    # Verdict Section
    story.append(Paragraph("Plagiarism Detection Verdict", subtitle_style))
    verdict_text = Paragraph(f"AI Generated Code Percentage: <b>{final_verdict:.2f}%</b>", styles['Normal'])
    story.append(verdict_text)
    story.append(Spacer(1, 6))
    
    # Code Section
    story.append(Paragraph("Uploaded Code Snippet", subtitle_style))
    code_para = Paragraph(code.replace('<', '&lt;').replace('>', '&gt;'), code_style)
    story.append(code_para)
    story.append(Spacer(1, 12))
    
    # Reasoning Section
    story.append(Paragraph("Detailed Analysis", subtitle_style))
    
   # Split reasoning into sections
    sections = reasoning.split('##')
    for section in sections[1:]:  # Skip the first empty section
        section_parts = section.split('\n', 1)
        section_title = section_parts[0].strip()
        section_content = section_parts[1].strip() if len(section_parts) > 1 else ""
        
        # Add section title
        story.append(Paragraph(section_title, styles['Heading3']))
        
        # Split section content into paragraphs
        paragraphs = section_content.split('\n')
        for para in paragraphs:
            if para.strip():
                # Check if it's a bullet point
                if para.strip().startswith('-'):
                    story.append(ListFlowable([
                        ListItem(Paragraph(para.strip('- ').strip(), styles['Normal']))
                    ]))
                else:
                    story.append(Paragraph(para.strip(), styles['Normal']))
                story.append(Spacer(1, 6))
    # Visualizations
    story.append(Paragraph("Visualization", subtitle_style))
    img_data = io.BytesIO(base64.b64decode(pie_histogram_base64))
    img = Image(img_data, width=6*inch, height=3*inch)
    story.append(img)

    doc.build(story)
    buffer.seek(0)
    return buffer
# FastAPI app setup
app = FastAPI()
router = APIRouter()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", response_class=HTMLResponse)
def read_root():
    return """
<html>
    <head>
        <style>
            body {
                font-family: Arial, sans-serif;
                background-color: #f4f4f9;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
            }
            h2 {
                color: #007BFF;
                text-align: center;
                margin-bottom: 20px;
            }
            .form-container {
                background-color: #ffffff;
                border-radius: 8px;
                padding: 20px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            }
            .input-group {
                margin-bottom: 15px;
            }
            input[type="file"], textarea, input[type="submit"] {
                width: 100%;
                padding: 10px;
                margin-top: 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
                font-size: 16px;
            }
            textarea {
                resize: vertical;
                height: 200px;
            }
            input[type="submit"] {
                background-color: #007BFF;
                color: white;
                font-size: 16px;
                border: none;
                cursor: pointer;
                transition: background-color 0.3s ease;
            }
            input[type="submit"]:hover {
                background-color: #0056b3;
            }
            .footer {
                text-align: center;
                margin-top: 20px;
            }
            .footer a {
                color: #007BFF;
                text-decoration: none;
            }
            .footer a:hover {
                text-decoration: underline;
            }
        </style>
    </head>
    <body>
        <h2>IntelliScan: AI Code Detection</h2>
        <div class="form-container">
            <h3>Upload File or Paste Code Snippet</h3>
            <form action="/analyze/" method="post" enctype="multipart/form-data">
                <div class="input-group">
                    <label for="file">Upload a file</label>
                    <input type="file" name="file" id="file">
                </div>
                <div class="input-group">
                    <label for="code_snippet">Or paste your code snippet here</label>
                    <textarea name="code_snippet" id="code_snippet" placeholder="Paste your code snippet..." rows="10"></textarea>
                </div>
                <div class="input-group">
                    <input type="submit" value="Analyze Code">
                </div>
            </form>
        </div>
        <div class="footer">
            <p>Need help? <a href="#">Contact us</a></p>
        </div>
    </body>
    </html>
    """

@router.post("/analyze/", response_class=HTMLResponse)
async def analyze_code(
    file: UploadFile = File(None),
    code_snippet: str = Form(None)
):
    if not file and not code_snippet:
        raise HTTPException(status_code=400, detail="No input provided. Please upload a file or paste a code snippet.")

    try:
        file_content = await file.read() if file else None
        filename = file.filename if file else "code_snippet"

        if code_snippet:
            filename = f"code_snippet_{len(analysis_results) + 1}.txt"

        # Process the input using the imported function
        processed_data = process_input(file_content=file_content, filename=filename, code_snippet=code_snippet)
        processed_code = processed_data["refined_text"]

        # Get AI and human percentages from Gemini model
        gemini_ai_percentage, gemini_human_percentage = get_gemini_percentages(processed_code)

        # Find top matches in Pinecone
        top_matches = find_top_matches(processed_code)

        # Calculate Pinecone percentages
        pinecone_ai_percentage, pinecone_human_percentage = calculate_pinecone_percentages(top_matches)
        
        # Calculate final verdict
        final_verdict = calculate_final_verdict(gemini_ai_percentage, pinecone_ai_percentage, pinecone_human_percentage)

        # Analyze code using Gemini model
        reasoning = analyze_code_with_gemini(processed_code, final_verdict)

        # Format the reasoning to HTML
        formatted_reasoning = format_gemini_response(reasoning)

        # Create visualizations
        pie_histogram_base64 = create_visualizations(final_verdict)

        # Generate PDF report
        pdf_report = generate_pdf_report(filename, processed_code, reasoning, final_verdict, pie_histogram_base64)

        # Store analysis results for later download
        analysis_results[filename] = {
            "code": processed_code,
            "reasoning": reasoning,
            "final_verdict": final_verdict,
            "pie_histogram_base64": pie_histogram_base64
        }

        # Create HTML response with the formatted reasoning
        response_html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Analysis Results</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            line-height: 1.6;
        }}
        .container {{
            background-color: #f9f9f9;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #333;
            text-align: center;
            border-bottom: 3px solid #007BFF;
            padding-bottom: 15px;
            font-size: 36px; /* Increased font size */
            font-weight: bold; /* Bold */
        }}
        h2 {{
            color: #007BFF;
            margin-top: 20px;
        }}
        h3 {{
            color: #007BFF;
            font-size: 28px; /* Increased font size */
            font-weight: bold; /* Bold */
            margin-top: 20px;
            text-align: center; /* Center alignment */
        }}
        .code-snippet {{
            background-color: #f4f4f4;
            border: 1px solid #ddd;
            border-radius: 4px;
            padding: 15px;
            overflow-x: auto;
            max-height: 300px;
            margin-bottom: 20px;
        }}
        .verdict {{
            text-align: center;
            font-size: 1.2em;
            margin: 20px 0;
            padding: 10px;
            background-color: #e9ecef;
            border-radius: 5px;
        }}
        .reasoning {{
            background-color: #ffffff;
            border-left: 4px solid #28a745;
            padding: 15px;
            margin: 20px 0;
        }}
        .reasoning h3 {{
            color: #28a745;
            margin-top: 0;
        }}
        .visualization {{
            text-align: center;
            margin: 20px 0;
        }}
        .action-buttons {{
            display: flex;
            justify-content: center;
            gap: 15px;
            margin-top: 20px;
        }}
        .action-buttons a {{
            display: inline-block;
            padding: 10px 15px;
            background-color: #007BFF;
            color: white;
            text-decoration: none;
            border-radius: 5px;
            transition: background-color 0.3s ease;
        }}
        .action-buttons a:hover {{
            background-color: #0056b3;
        }}
        /* To hide the download button */
        #downloadButton {{
            display: none;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>IntelliScan: Code Analysis Report</h1>
        
        <h2>Uploaded Code Snippet</h2>
        <div class="code-snippet">
            <pre>{processed_code}</pre>
        </div>
        
        <div class="verdict">
            <strong>Final Verdict on AI Code Detection:</strong> {final_verdict:.2f}%
        </div>
        
        <div class="reasoning">
            <h3>Detailed Analysis</h3>
            {formatted_reasoning}
        </div>
        
        <div class="visualization">
            <h3>Visualizations</h3>
            <img src="data:image/png;base64,{pie_histogram_base64}" alt="AI vs Human Code Visualization" style="max-width: 100%; height: auto;"/>
        </div>
        
        <div class="action-buttons">
            <a href="/download/{filename}" id="downloadButton">Download PDF Report</a>
            <a href="/">Analyze Another Code Snippet</a>
        </div>
    </div>
</body>
</html>
"""


        return HTMLResponse(content=response_html)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    
def extract_section(text, section_name):
    sections = text.split('##')
    for section in sections:
        if section.startswith(section_name):
            return section.split('\n', 1)[1].strip()
    return "No details available"

def create_list_items(text, section_name):
    sections = text.split('##')
    for section in sections:
        if section.startswith(section_name):
            content = section.split('\n', 1)[1].strip()
            list_items = [f"<li>{item.strip('- ')}</li>" for item in content.split('\n') if item.strip().startswith('-')]
            return '\n'.join(list_items)
    return ""    



@router.get("/download/{file_name}")
async def download_report(file_name: str):
    if file_name not in analysis_results:
        raise HTTPException(status_code=404, detail="Report not found")

    result = analysis_results[file_name]
    pdf_buffer = generate_pdf_report(
        file_name, 
        result["code"], 
        result["reasoning"], 
        result["final_verdict"], 
        result["pie_histogram_base64"]
    )

    return StreamingResponse(pdf_buffer, media_type='application/pdf', headers={"Content-Disposition": f"attachment; filename={file_name.split('.')[0]}_report_intelliscan.pdf"})

# Include the router
app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=4003, reload=True)