const requestButton = document.querySelector("#request-button");
const buttonLabel = document.querySelector("#button-label");
const responseArea = document.querySelector("#response-area");
const resumeInput = document.querySelector("#resume-input");
const fileNameDisplay = document.querySelector("#file-name-display");

resumeInput.addEventListener("change", () => {
  if (resumeInput.files.length) {
    fileNameDisplay.textContent = resumeInput.files[0].name;
  } else {
    fileNameDisplay.textContent = "Choose resume (PDF or DOCX)";
  }
});

function showResponse(content, type = "success") {
  if (type === "error") {
    responseArea.innerHTML = `<p class="error-text">${content}</p>`;
    return;
  }

  responseArea.innerHTML = `
    <span class="response-label">Your recommendation</span>
    <p class="response-text"></p>
  `;
  responseArea.querySelector(".response-text").textContent = content;
}

async function requestRecommendation() {
  if (!resumeInput.files.length) {
    showResponse("Please choose a resume file first.", "error");
    return;
  }

  requestButton.disabled = true;
  buttonLabel.textContent = "Searching your best matches...";
  responseArea.innerHTML = `
    <div class="response-placeholder">
      <span class="placeholder-icon" aria-hidden="true">...</span>
      <span>Reviewing your career profile</span>
    </div>
  `;

  const formData = new FormData();
  formData.append("resume", resumeInput.files[0]);

  try {
    const response = await fetch("http://127.0.0.1:8000/execute-workflow", {
      method: "POST",
      body: formData
    });

    if (!response.ok) {
      throw new Error(`Request failed with status ${response.status}.`);
    }

    const data = await response.json();

    if (data.error) {
      showResponse(data.error, "error");
    } else {
      showResponse(data.result || "No recommendation was returned. Please try again.");
    }
  } catch (error) {
    showResponse("I could not reach the career service. Make sure the API is running and try again.", "error");
  } finally {
    requestButton.disabled = false;
    buttonLabel.textContent = "Find my opportunities";
  }
}

requestButton.addEventListener("click", requestRecommendation);