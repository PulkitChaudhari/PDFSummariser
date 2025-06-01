const dragDropArea = document.getElementById("drag-drop-area");
const fileInput = document.getElementById("file-upload");
const form = document.getElementById("upload-form");
const loading = document.querySelector(".loading");
const error = document.querySelector(".error");
const summary = document.getElementById("summary");
const hireInput = document.getElementById("hireInput");

// Global variable to store the current approval promise
let currentApprovalPromise = null;

// Function to get user approval via buttons
function getHumanApproval() {
  return new Promise((resolve) => {
    const yesButton = hireInput.querySelector("button:first-child");
    const noButton = hireInput.querySelector("button:last-child");

    const handleYes = () => {
      yesButton.removeEventListener("click", handleYes);
      noButton.removeEventListener("click", handleNo);
      resolve("Y");
    };

    const handleNo = () => {
      yesButton.removeEventListener("click", handleYes);
      noButton.removeEventListener("click", handleNo);
      resolve("N");
    };

    yesButton.addEventListener("click", handleYes);
    noButton.addEventListener("click", handleNo);
  });
}

function showLoading() {
  loading.style.display = "block";
  error.style.display = "none";
  summary.style.display = "none";
  hireInput.style.display = "none";
}

function showError(message) {
  loading.style.display = "none";
  error.style.display = "block";
  error.textContent = message;
  summary.style.display = "none";
  hireInput.style.display = "none";
}

function showSummary(text) {
  loading.style.display = "none";
  error.style.display = "none";
  summary.style.display = "block";
  summary.textContent = text;
}

function showApprovalPrompt() {
  hireInput.style.display = "block";
}

async function handleFileUpload(file) {
  const formData = new FormData();
  formData.append("pdf", file);

  try {
    showLoading();
    const response = await fetch("/", {
      method: "POST",
      body: formData,
    });
    const data = await response.json();
    if (data.status === "success") {
      showSummary(data.summary);
      if (data.requires_approval) {
        showApprovalPrompt();
        const decision = await getHumanApproval();
        const decisionResponse = await fetch("/decision/", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ decision }),
        });
        const decisionData = await decisionResponse.json();
        if (decisionData.status === "success") {
          showSummary(decisionData.message);
        } else {
          showError(decisionData.message || "Error processing decision");
        }
      }
    } else {
      showError(data.message || "An error occurred while processing the file.");
    }
  } catch (err) {
    showError("Failed to upload file. Please try again.");
  }
}

dragDropArea.addEventListener("click", (e) => {
  // Only trigger file input if the click is directly on the drag-drop area
  // and not on any child elements
  if (e.target === dragDropArea) {
    fileInput.click();
  }
});

dragDropArea.addEventListener("dragover", (e) => {
  e.preventDefault();
  dragDropArea.classList.add("dragover");
});

dragDropArea.addEventListener("dragleave", (e) => {
  e.preventDefault();
  dragDropArea.classList.remove("dragover");
});

dragDropArea.addEventListener("drop", (e) => {
  e.preventDefault();
  dragDropArea.classList.remove("dragover");
  if (e.dataTransfer.files.length) {
    handleFileUpload(e.dataTransfer.files[0]);
  }
});

fileInput.addEventListener("change", () => {
  if (fileInput.files.length) {
    handleFileUpload(fileInput.files[0]);
  }
});
