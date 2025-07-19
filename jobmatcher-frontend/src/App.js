import React, { useState, useEffect } from "react";
import axios from "axios";
import "./App.css";

function App() {
  const [skills, setSkills] = useState("");
  const [desiredJobs, setDesiredJobs] = useState("");
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const validateFile = (file) => {
    const maxSize = 10 * 1024 * 1024;
    const allowedTypes = [
      "application/pdf",
      "application/msword",
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
      "image/jpeg",
      "image/jpg",
      "image/png",
      "text/plain",
    ];
    if (file.size > maxSize) return "File must be smaller than 10MB.";
    if (!allowedTypes.includes(file.type)) return "Unsupported file type.";
    return null;
  };

  const handleFileSelect = (selectedFile) => {
    if (!selectedFile) return;
    const validationError = validateFile(selectedFile);
    if (validationError) return setError(validationError);
    setFile(selectedFile);
    setError("");
  };

  const handleSubmit = async () => {
    if (!skills.trim() && !file)
      return setError("Provide skills or upload a CV/resume.");
    if (skills.trim() && skills.trim().length < 3)
      return setError("Minimum 3 characters required for skills.");

    setLoading(true);
    setError("");
    setResult(null);

    const formData = new FormData();
    if (skills.trim()) formData.append("skills", skills.trim());
    if (desiredJobs.trim()) formData.append("desired_jobs", desiredJobs.trim());
    if (file) formData.append("file", file);

    try {
      const response = await axios.post(`/match-jobs`, formData, {
        headers: { "Content-Type": "multipart/form-data" },
        timeout: 30000,
      });

      setResult(response.data || null);
      if (!response.data) setError("No response data.");
    } catch (err) {
      if (err.code === "ECONNABORTED") setError("Request timed out.");
      else if (err.response)
        setError(`Server error: ${err.response.data?.message || err.response.statusText}`);
      else setError("Network error. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (result) console.log("🔍 Gemini result:", result);
  }, [result]);

  return (
    <main className="app">
      <div className="card">
        <h1>Job Readiness Analyzer</h1>

        <label htmlFor="skills">Your Skills</label>
        <textarea
          id="skills"
          placeholder="e.g., JavaScript, HTML, CSS"
          value={skills}
          onChange={(e) => setSkills(e.target.value)}
        />

        <label htmlFor="jobs">Desired Job Roles</label>
        <textarea
          id="jobs"
          placeholder="e.g., Frontend Developer, UI Designer"
          value={desiredJobs}
          onChange={(e) => setDesiredJobs(e.target.value)}
        />

        <input
          type="file"
          accept=".pdf,.doc,.docx,.jpg,.jpeg,.png,.txt"
          onChange={(e) => handleFileSelect(e.target.files[0])}
        />

        <button onClick={handleSubmit} disabled={loading}>
          {loading ? "Analyzing..." : "Analyze"}
        </button>

        {error && <p className="error">{error}</p>}

        {result && !result.error && (
          <section className="results">
            <h2>📊 Results Overview</h2>

            {[
              ["Current Skills", result.current_skills],
              ["Missing Skills", result.missing_skills],
              ["Recommended Certifications", result.recommended_certifications],
              ["Effort Level", result.effort_level],
              ["Summary Advice", result.summary_advice],
              ["Jobs You Can Apply For", result.job_roles_you_can_apply_for],
              ["Aspirational Roles", result.job_roles_you_desire],
              ["Match Percentage", `${result.percentage_match ?? 0}%`],
              ["Strong CV Points", result.cv_strong_points, result.used_cv],
              ["Weak CV Points", result.cv_weak_points, result.used_cv],
              ["CV Suggestions", result.cv_improvement_suggestions, result.used_cv],
              ["Market Trend Advice", result.market_trend_advice],
            ].map(([title, content, show = true], i) =>
              show && (Array.isArray(content) || typeof content === "string" || typeof content === "number") ? (
                <div key={i} className="section">
                  <h3>{title}</h3>
                  {Array.isArray(content) ? (
                    content.length > 0 ? (
                      <ul>
                        {content.map((item, idx) => (
                          <li key={idx}>
                            {typeof item === "object" && item.name
                              ? `${item.name} (${item.provider})`
                              : item}
                          </li>
                        ))}
                      </ul>
                    ) : (
                      <p style={{ fontStyle: "italic", color: "#888" }}>
                        No {title.toLowerCase()} identified yet.
                      </p>
                    )
                  ) : content ? (
                    <p>{content}</p>
                  ) : (
                    <p style={{ fontStyle: "italic", color: "#888" }}>
                      No {title.toLowerCase()} provided.
                    </p>
                  )}
                </div>
              ) : null
            )}

            {result.recommended_courses?.length > 0 && (
              <div className="section">
                <h3>Recommended Courses</h3>
                <ul>
                  {result.recommended_courses.map((course, i) => {
                    if (typeof course === "string") return <li key={i}>{course}</li>;
                    if (course.missing_skill && Array.isArray(course.courses)) {
                      return (
                        <li key={i}>
                          <strong>{course.missing_skill}</strong>
                          <ul>
                            {course.courses.map((c, j) => (
                              <li key={j}>{c}</li>
                            ))}
                          </ul>
                        </li>
                      );
                    }
                    return null;
                  })}
                </ul>
              </div>
            )}
          </section>
        )}
      </div>
    </main>
  );
}

export default App;