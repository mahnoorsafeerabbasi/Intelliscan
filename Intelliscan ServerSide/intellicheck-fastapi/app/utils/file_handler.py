# app/utils/file_handler.py

import shutil
import os
from copydetect import CopyDetector

def handle_files(files, upload_directory):
    os.makedirs(upload_directory, exist_ok=True)

    # Clear the upload directory to avoid including old files
    for filename in os.listdir(upload_directory):
        file_path = os.path.join(upload_directory, filename)
        if os.path.isfile(file_path):
            os.remove(file_path)

    # Save uploaded files
    file_paths = []
    for file in files:
        file_path = os.path.join(upload_directory, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        file_paths.append(file_path)
    
    return file_paths

def run_detection(file_paths):
    # Get the path to the Downloads folder
    downloads_folder = os.path.join(os.getenv("USERPROFILE"), "Downloads")
    os.makedirs(downloads_folder, exist_ok=True)

    # Define temporary and final report paths
    temp_report_path = os.path.join(downloads_folder, "temp_report.html")
    final_report_path = os.path.join(downloads_folder, "report.html")
    
    # Create the CopyDetector instance
    detector = CopyDetector(
        test_dirs=[],  # Not needed for direct file comparison
        ref_dirs=[],   # Not needed for direct file comparison
        display_t=0.5,
        autoopen=False,
        out_file=temp_report_path  # Path to save temporary report
    )

    # Add each file as both test and reference for cross-comparison
    for i, file_path in enumerate(file_paths):
        for j, other_file_path in enumerate(file_paths):
            if i != j:
                detector.add_file(file_path, type='test')
                detector.add_file(other_file_path, type='ref')

    detector.run()
    detector.generate_html_report(output_mode='save')

    # Move the temporary report to the final location
    shutil.move(temp_report_path, final_report_path)

    return final_report_path
