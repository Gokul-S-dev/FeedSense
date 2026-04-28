import axios from 'axios';
import React, { useState } from 'react';
import './Input.css';

const Input = () => {
    const [feedback, setFeedback] = useState("");
    const [loading, setLoading] = useState(false);
    const [success, setSuccess] = useState(false);
    const [error, setError] = useState(null);
    const [charCount, setCharCount] = useState(0);

    const handleChange = (e) => {
        const value = e.target.value;
        setFeedback(value);
        setCharCount(value.length);
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!feedback.trim()) {
            setError("Please enter your feedback");
            return;
        }

        setLoading(true);
        setError(null);
        setSuccess(false);

        try {
const res = await axios.post(
  "https://8ur8lkoioe.execute-api.us-east-1.amazonaws.com/deploy",
  {
    feedback: feedback
  },
  {
    headers: {
      "Content-Type": "application/json"
    }
  }
);
            console.log(res.data);
            setSuccess(true);
            setFeedback("");
            setCharCount(0);
            setTimeout(() => setSuccess(false), 4000);
        } catch (err) {
            console.log(err);
            setError(err.message || "Failed to submit feedback. Please try again.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="feedback-container">
            <div className="feedback-wrapper">
                {/* Header Section */}
                <div className="feedback-header">
                    <div className="header-icon">✨</div>
                    <h1 className="feedback-title">Share Your Feedback</h1>
                    <p className="feedback-subtitle">
                        Help us improve by sharing your thoughts, suggestions, or concerns
                    </p>
                </div>

                {/* Form Section */}
                <form onSubmit={handleSubmit} className="feedback-form">
                    <div className="form-group">
                        <div className="textarea-wrapper">
                            <textarea
                                className={`feedback-textarea ${error ? 'error' : ''}`}
                                placeholder="Tell us what you think... (minimum 10 characters)"
                                value={feedback}
                                onChange={handleChange}
                                rows="8"
                                minLength="10"
                            />
                            <div className="textarea-border"></div>
                        </div>

                        {/* Character Count */}
                        <div className="char-counter">
                            <span className={charCount > 0 ? 'active' : ''}>
                                {charCount} characters
                            </span>
                        </div>
                    </div>

                    {/* Error Message */}
                    {error && (
                        <div className="feedback-alert error-alert">
                            <span className="alert-icon">⚠️</span>
                            <span>{error}</span>
                        </div>
                    )}

                    {/* Success Message */}
                    {success && (
                        <div className="feedback-alert success-alert">
                            <span className="alert-icon">✓</span>
                            <span>Thank you! Your feedback has been submitted successfully.</span>
                        </div>
                    )}

                    {/* Submit Button */}
                    <button
                        type="submit"
                        className={`submit-btn ${loading ? 'loading' : ''} ${success ? 'success' : ''}`}
                        disabled={loading || !feedback.trim()}
                    >
                        {loading ? (
                            <>
                                <span className="spinner"></span>
                                Submitting...
                            </>
                        ) : success ? (
                            <>
                                <span className="checkmark">✓</span>
                                Submitted
                            </>
                        ) : (
                            <>
                                <span className="send-icon">→</span>
                                Submit Feedback
                            </>
                        )}
                    </button>
                </form>

                {/* Info Box */}
                <div className="info-box">
                    <p>
                        💡 <strong>Tip:</strong> Specific, detailed feedback helps us understand your needs better.
                    </p>
                </div>
            </div>

            {/* Decorative Elements */}
            <div className="decoration decoration-1"></div>
            <div className="decoration decoration-2"></div>
        </div>
    );
};

export default Input;