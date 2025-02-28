# Intellicheck: Plagiarism Detection for Student Code

## Overview

**Intellicheck** is a plagiarism detection tool specifically designed to analyze student code files and detect instances of code similarity, which may indicate plagiarism. The tool utilizes a **machine learning-based model** based on **linear regression** to compare different code files and determine the likelihood that they share significant similarities. The model was initially pre-built by [CopyDetect](https://github.com/blingenf/copydetect.git), and Intellicheck has customized it by adjusting the thresholds for detecting plagiarism in student submissions.

Intellicheck is built to provide a web-based interface for detecting plagiarism across various programming languages, such as Python, Java, C++, and JavaScript. The FastAPI server allows students and educators to upload code files and receive an analysis of plagiarism, helping to ensure academic integrity in coding assignments.

---

## Features

- **Plagiarism Detection**: Detects plagiarism between student code files using machine learning techniques.
- **Linear Regression Model**: Uses a customized linear regression model to compare code files for similarities.
- **Threshold Customization**: The plagiarism detection thresholds have been fine-tuned to suit academic use cases, making it sensitive enough for student assignments.
- **FastAPI Interface**: Provides a user-friendly API to upload code files and receive plagiarism analysis.
- **Multi-language Support**: Detects plagiarism for popular programming languages like Python, Java, C++, and JavaScript.

---

## Why Intellicheck?

Intellicheck is built to help educators and students ensure that code submissions are original and not plagiarized. The model analyzes code syntax, structure, and logic to compute a similarity score, which can then be used to determine whether the code was copied or written independently.

By leveraging **linear regression** and adjusting plagiarism thresholds based on the context of academic submissions, Intellicheck ensures a balance between accuracy and sensitivity. It's designed for use in educational settings, such as universities or coding boot camps, where academic integrity is paramount.

---

## Technologies Used

- **FastAPI**: A modern web framework for building APIs with Python.
- **Machine Learning Model**: Custom linear regression model for plagiarism detection.
- **Python 3.x**: The programming language used to build the application.
- **Pydantic**: For data validation.
- **Uvicorn**: ASGI server for running the FastAPI application.
- **GitHub (copydetect)**: Original model pre-built by [blingenf/copydetect](https://github.com/blingenf/copydetect.git).

---

## Setup and Installation

### Prerequisites

- **Python 3.x** (preferably 3.7+)
- **Prebuilt Linear Regression Model**: We use a modified version of the model from [copydetect](https://github.com/blingenf/copydetect.git).
  
