"use client"; // This line marks the component as a Client Component

import { useState } from 'react';
import Head from 'next/head';
import Image from 'next/image';
import styles from './JavaPage.module.css'; // Adjust the import as necessary
import BackgroundImage from "@/images/background-call-to-action.jpg"

export default function CppPage() {
  const [file, setFile] = useState(null);
  const [codeSnippet, setCodeSnippet] = useState('');
  const [response, setResponse] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [fileName, setFileName] = useState(''); // State for storing the filename
  const [pdfUrl, setPdfUrl] = useState(null); // State for the PDF URL

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    setFile(selectedFile);
    setFileName(selectedFile ? selectedFile.name : ''); // Set the filename
  };

  const handleSnippetChange = (e) => {
    setCodeSnippet(e.target.value);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const formData = new FormData();

    if (file) {
      formData.append('file', file);
    }
    if (codeSnippet) {
      formData.append('code_snippet', codeSnippet);
    }

    setIsLoading(true); // Set loading to true when submission starts
    setPdfUrl(null);  // Reset PDF URL

    try {
      const res = await fetch('http://localhost:4002/analyze/', {
        method: 'POST',
        body: formData,
      });

      if (!res.ok) {
        throw new Error(`HTTP error! status: ${res.status}`);
      }

      const data = await res.text();
      setResponse(data);

      // Extract the filename from the response to create the PDF download URL
      const match = data.match(/\/download\/(.*?)"/);
      if (match && match[1]) {
        const extractedFileName = match[1];
        setFileName(extractedFileName);
        setPdfUrl(`http://localhost:4002/download/${extractedFileName}`);
      }
    } catch (error) {
      setResponse(`Error: ${error.message}`);
    } finally {
      setIsLoading(false); // Set loading to false when done
    }
  };

  const handleDownload = async () => {
    if (!pdfUrl) return;

    try {
      const response = await fetch(pdfUrl);
      if (!response.ok) {
        throw new Error('Failed to download report');
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${fileName.split('.')[0]}_report_intelliscan.pdf`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Download error:', error);
    }
  };

  return (
    <div className='relative'>
      <Head>
        <title>Check Java Plagiarism</title>
      </Head>
      <Image
        className="absolute inset-0 w-full h-full object-cover z-[-1]"
        src={BackgroundImage}
        alt="Background"
        layout="fill"
        quality={100}
        style={{ filter: "blur(20px)" }}
      />
      <div className="flex flex-col items-center justify-center min-h-screen  p-4 gap-4">
        <h1 className="text-5xl font-bold mb-8" style={{ fontFamily: "Arial, sans-serif" }}>
          <div className="bg-white py-3 px-6 rounded-full shadow-lg flex justify-center items-center">
            <span className="text-gray-800 font-bold">Check Java</span>
            <span className="text-blue-800 font-bold">Plagiarism</span>
          </div>
        </h1>
        <form onSubmit={handleSubmit} className="flex flex-col space-y-4 w-full max-w-md">
          <label htmlFor="file-upload" className={styles.label}>
            Choose File
          </label>
          <input
            id="file-upload"
            type="file"
            accept=".cpp, .png, .jpg, .jpeg, .gif, .pdf, .docx"
            onChange={handleFileChange}
            className={styles.hiddenFileInput}
          />
          <textarea
            value={codeSnippet}
            onChange={handleSnippetChange}
            placeholder="Paste your java code snippet here..."
            className={styles.textarea}
          />
          <button
            type="submit"
            className="bg-black text-white font-semibold py-3 px-6 rounded-full shadow-md hover:bg-[#3c3744]  transition duration-300"
          >
            Submit
          </button>
        </form>
        {isLoading && (
          <div className={styles.analyzing}>
            <div>Analyzing Please Wait</div>
            <div className={styles.analyzingContainer}>
              <span className={styles.dot}></span>
              <span className={styles.dot}></span>
              <span className={styles.dot}></span>
            </div>
          </div>
        )}

        {response && (
          <div className={`${styles.responseContainer} mt-4 p-4 bg-white shadow-md rounded-lg`}>
            <div dangerouslySetInnerHTML={{ __html: response }} />
            {pdfUrl && (
              <button 
                onClick={handleDownload} 
                className="mt-4 bg-[#3066be] text-white font-semibold py-3 px-6 rounded-lg shadow-md hover:bg-[#3c3744] transition duration-300"
              >
                Download Report
              </button>
            )}
          </div>
        )}
      </div>
    </div>
  );
}