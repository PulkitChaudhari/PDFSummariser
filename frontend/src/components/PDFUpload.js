import React, { useState, useRef } from "react";
import {
  Box,
  Button,
  Typography,
  Paper,
  CircularProgress,
} from "@mui/material";
import axios from "axios";

// Configure axios defaults
axios.defaults.withCredentials = true;

const PDFUpload = () => {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [summary, setSummary] = useState("");
  const [showApproval, setShowApproval] = useState(false);
  const fileInputRef = useRef(null);

  const handleFileChange = (event) => {
    const selectedFile = event.target.files[0];
    if (selectedFile && selectedFile.type === "application/pdf") {
      setFile(selectedFile);
      setError("");
    } else {
      setError("Please select a valid PDF file");
      setFile(null);
    }
  };

  const handleDragOver = (event) => {
    event.preventDefault();
    event.currentTarget.classList.add("dragover");
  };

  const handleDragLeave = (event) => {
    event.preventDefault();
    event.currentTarget.classList.remove("dragover");
  };

  const handleDrop = (event) => {
    event.preventDefault();
    event.currentTarget.classList.remove("dragover");

    const droppedFile = event.dataTransfer.files[0];
    if (droppedFile && droppedFile.type === "application/pdf") {
      setFile(droppedFile);
      setError("");
    } else {
      setError("Please drop a valid PDF file");
    }
  };

  const handleUpload = async () => {
    if (!file) return;

    const formData = new FormData();
    formData.append("pdf", file);

    setLoading(true);
    setError("");
    setSummary("");
    setShowApproval(false);

    try {
      const response = await fetch("http://127.0.0.1:8081/api/upload", {
        method: "POST",
        body: formData,
      });

      const data = await response.json();

      if (data.status === "success") {
        setSummary(data.summary);
        if (data.requires_approval) {
          setShowApproval(true);
        }
      } else {
        setError(data.message || "An error occurred");
      }
    } catch (err) {
      console.error("Upload error:", err);
      setError(err.message || "Failed to upload file");
    } finally {
      setLoading(false);
    }
  };

  const handleDecision = async (decision) => {
    try {
      const response = await fetch("http://127.0.0.1:8081/api/decision", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ decision }),
      });

      const data = await response.json();

      if (data.status === "success") {
        setSummary(data.message);
        setShowApproval(false);
      } else {
        setError(data.message || "Error processing decision");
      }
    } catch (err) {
      console.error("Decision error:", err);
      setError(err.message || "Failed to process decision");
    }
  };

  return (
    <Box sx={{ maxWidth: 600, mx: "auto", p: 3 }}>
      <Paper
        sx={{
          p: 3,
          textAlign: "center",
          cursor: "pointer",
          border: "2px dashed #ccc",
          "&.dragover": {
            borderColor: "primary.main",
            backgroundColor: "action.hover",
          },
        }}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
      >
        <input
          type="file"
          accept=".pdf"
          onChange={handleFileChange}
          style={{ display: "none" }}
          ref={fileInputRef}
        />
        <Typography variant="h6" gutterBottom>
          Drag and drop a PDF file here or click to select
        </Typography>
        {file && (
          <Typography variant="body2" color="text.secondary">
            Selected file: {file.name}
          </Typography>
        )}
      </Paper>

      {error && (
        <Typography color="error" sx={{ mt: 2 }}>
          {error}
        </Typography>
      )}

      {file && (
        <Button
          variant="contained"
          onClick={handleUpload}
          disabled={loading}
          sx={{ mt: 2 }}
        >
          Upload
        </Button>
      )}

      {loading && (
        <Box sx={{ display: "flex", justifyContent: "center", mt: 2 }}>
          <CircularProgress />
        </Box>
      )}

      {summary && (
        <Paper sx={{ mt: 2, p: 2 }}>
          <Typography variant="h6" gutterBottom>
            Summary
          </Typography>
          <Typography>{summary}</Typography>
        </Paper>
      )}

      {showApproval && (
        <Box sx={{ mt: 2, display: "flex", gap: 2, justifyContent: "center" }}>
          <Button
            variant="contained"
            color="success"
            onClick={() => handleDecision("Y")}
          >
            Yes
          </Button>
          <Button
            variant="contained"
            color="error"
            onClick={() => handleDecision("N")}
          >
            No
          </Button>
        </Box>
      )}
    </Box>
  );
};

export default PDFUpload;
