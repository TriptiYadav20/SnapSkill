// File: src/components/ATSChecker.jsx
import React, { useState } from "react";
import "../styles/ATSChecker.css";
import atsImage from "../assets/ATSUI.webp";
import { CloudUpload, CheckCircle, XCircle } from "lucide-react";
import { CircularProgressbar, buildStyles } from "react-circular-progressbar";
import "react-circular-progressbar/dist/styles.css";

const ATSChecker = () => {
  const [score, setScore] = useState(null);
  const [resume, setResume] = useState(null);
  const [keywords, setKeywords] = useState({ matched: [], missing: [] });

  const handleUpload = async (e) => {
    const file = e.target.files[0];
    setResume(file);
    const formData = new FormData();
    formData.append("resume", file);

    const res = await fetch("http://localhost:5000/match", {
      method: "POST",
      body: formData,
    });

    const data = await res.json();
    setScore(data.score);
    setKeywords({
      matched: data.matched_keywords,
      missing: data.missing_keywords,
    });
  };

  const getScoreColor = (value) => {
    if (value >= 80) return "#28a745";
    if (value >= 50) return "#ffc107";
    return "#dc3545";
  };

  return (
    <div className="ats-wrapper">
      <div className="ats-left">
        <h1>Is Your Resume ATS-Friendly?</h1>
        <p>
          Upload your resume to evaluate how well it matches an ideal job
          description and receive AI-powered tips to enhance it.
        </p>

        <label className="upload-label">
          <CloudUpload style={{ marginRight: "10px", verticalAlign: "middle" }} />
          Upload Your Resume
          <input type="file" accept=".pdf" onChange={handleUpload} hidden />
        </label>

        {score !== null && (
          <div className="score-preview">
            <div style={{ width: 100, height: 100 }}>
              <CircularProgressbar
                value={score}
                text={`${score}%`}
                styles={buildStyles({
                  pathColor: getScoreColor(score),
                  textColor: "#333",
                  trailColor: "#eee",
                  textSize: "18px",
                })}
              />
            </div>
            <p className="score-label">Match Score</p>
          </div>
        )}

        {keywords.matched.length > 0 && (
          <div className="keyword-section">
            <h3><CheckCircle color="#28a745" size={20} style={{ marginRight: 5 }} /> Matched Keywords</h3>
            <div className="keyword-chips green">
              {keywords.matched.map((word, idx) => (
                <span key={idx}>{word}</span>
              ))}
            </div>
          </div>
        )}

        {keywords.missing.length > 0 && (
          <div className="keyword-section">
            <h3><XCircle color="#dc3545" size={20} style={{ marginRight: 5 }} /> Missing Keywords</h3>
            <div className="keyword-chips red">
              {keywords.missing.map((word, idx) => (
                <span key={idx}>{word}</span>
              ))}
            </div>
          </div>
        )}
      </div>

      <div className="ats-right">
        <img src={atsImage} alt="Resume Visual" />
      </div>
    </div>
  );
};

export default ATSChecker;
