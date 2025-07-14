// File: src/components/ResumeEnhancer.jsx
import React, { useState } from "react";
import "../styles/ResumeEnhancer.css";
import { Sparkles } from "lucide-react";
import enhancerImage from "../assets/EnhancerUi.webp";

const ResumeEnhancer = () => {
  const [suggestions, setSuggestions] = useState([]);
  const [enhancedPdf, setEnhancedPdf] = useState(null);

  const handleUpload = async (e) => {
    const file = e.target.files[0];
    const formData = new FormData();
    formData.append("resume", file);

    const res = await fetch("http://localhost:5001/enhance", {
      method: "POST",
      body: formData,
    });

    const data = await res.json();

    // Decode base64 PDF
    if (data.enhanced_pdf) {
      const byteCharacters = atob(data.enhanced_pdf);
      const byteNumbers = new Array(byteCharacters.length).fill(0).map((_, i) => byteCharacters.charCodeAt(i));
      const byteArray = new Uint8Array(byteNumbers);
      const blob = new Blob([byteArray], { type: "application/pdf" });
      const url = URL.createObjectURL(blob);
      setEnhancedPdf(url);
    }

    setSuggestions(data.suggestions || []);
  };

  return (
    <div className="enhancer-container" style={{
      display: "flex",
      justifyContent: "space-between",
      alignItems: "center",
      background: "linear-gradient(to right, #fdfbfb, #ebedee)",
      padding: "2rem",
      borderRadius: "16px",
      gap: "2rem",
      flexWrap: "wrap"
    }}>
      <div className="enhancer-left" style={{ flex: "1", minWidth: "300px" }}>
        <h1 style={{ fontSize: "2rem", fontWeight: "700" }}>Want to improve your resume?</h1>
        <p style={{ maxWidth: "500px", marginTop: "0.75rem", color: "#333" }}>
          Upload your resume and see how it can be transformed with our AI-powered suggestions.
          We’ll enhance formatting, keywords, and overall structure to maximize ATS success.
        </p>

        <label
          className="enhancer-upload"
          style={{
            border: "2px dashed #9333ea",
            color: "#6b21a8",
            padding: "0.9rem 1.4rem",
            borderRadius: "12px",
            cursor: "pointer",
            display: "inline-block",
            marginTop: "1.5rem",
            fontWeight: 500,
          }}
        >
          <Sparkles style={{ marginRight: "8px", verticalAlign: "middle" }} />
          Upload Resume
          <input type="file" accept=".pdf" onChange={handleUpload} hidden />
        </label>

        {suggestions.length > 0 && (
          <div className="suggestion-box" style={{ marginTop: "1.5rem", background: "#fef9ff", padding: "1rem", borderRadius: "10px", border: "1px solid #e9d5ff" }}>
            <h3 style={{ marginBottom: "0.5rem", color: "#6b21a8" }}>✨ AI Suggestions:</h3>
            <ul style={{ paddingLeft: "1.2rem", color: "#444", lineHeight: "1.5" }}>
              {suggestions.map((s, idx) => (
                <li key={idx}>{s}</li>
              ))}
            </ul>
          </div>
        )}

        {enhancedPdf && (
          <a
            href={enhancedPdf}
            download="Enhanced_Resume.pdf"
            className="download-btn"
            style={{
              marginTop: "1.2rem",
              display: "inline-block",
              backgroundColor: "#6b21a8",
              color: "white",
              padding: "0.6rem 1.2rem",
              borderRadius: "8px",
              textDecoration: "none",
              fontWeight: "bold",
            }}
          >
            📄 Download Enhanced Resume
          </a>
        )}
      </div>

      <div className="enhancer-right" style={{ flex: "1", textAlign: "center", minWidth: "300px" }}>
        <img src={enhancerImage} alt="Resume Visual" style={{ maxWidth: "75%", borderRadius: "12px", boxShadow: "0 4px 14px rgba(0,0,0,0.1)" }} />
      </div>
    </div>
  );
};

export default ResumeEnhancer;
