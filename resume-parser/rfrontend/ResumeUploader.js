import React, { useState } from "react";

function ResumeUploader() {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState("");
  const [error, setError] = useState("");

  const API_URL = process.env.REACT_APP_API_URL || "http://localhost:5000";

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleUpload = async () => {
    if (!file) {
      setError("Please choose a file first.");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    try {
      setError("");
      setResult("Processing...");
      const response = await fetch(`${API_URL}/extract`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error("Error from server");
      }

      const data = await response.json();
      setResult(JSON.stringify(data, null, 2));
    } catch (err) {
      setError("Something went wrong. Please try again.");
      setResult("");
    }
  };

  return (
    <div className="App">
      <h1>Resume Parser</h1>
      <p>Upload your resume and extract skills automatically.</p>
      <input type="file" onChange={handleFileChange} />
      <button onClick={handleUpload}>Upload & Extract</button>

      {error && <p style={{ color: "red" }}>{error}</p>}
      {result && <pre>{result}</pre>}
    </div>
  );
}

export default ResumeUploader;
