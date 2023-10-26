document.addEventListener("DOMContentLoaded", function () {
  const uploadButton = document.getElementById("upload-button");
  const fileInput = document.getElementById("file-input");
  const promptInputs = document.getElementsByClassName("prompt-input");
  const resultsContainer = document.getElementById("results");
  const loadingContainer = document.getElementById("loading");
  const addPromptButton = document.getElementById("add-prompt-button");
  

  uploadButton.addEventListener("click", () => {
    const formData = new FormData();

    const jobDescription = document.getElementById("job-description").value;
    formData.append("job_description", jobDescription);

    for (let i = 0; i < fileInput.files.length; i++) {
      formData.append("file", fileInput.files[i]);
    }

    for (let i = 0; i < promptInputs.length; i++) {
      formData.append("prompt", promptInputs[i].value);
    }

    // Show loading
    loadingContainer.style.display = "block";

    axios
      .post("http://localhost:5000/upload", formData)
      .then((res) => {
        resultsContainer.innerHTML = ""; // Limpa resultados anteriores
        for (const [fileName, results] of Object.entries(res.data)) {
          const fileDiv = document.createElement("div");
          fileDiv.innerHTML = `<strong>Arquivo:</strong> ${fileName} <br>`;
          for (const result of results) {
            const resultDiv = document.createElement("div");
            resultDiv.innerHTML = `
            <strong>Tecnologia:</strong> ${result.prompt} <br>
            <strong>Resultado:</strong> ${result.approval} <br>
            <details>
              <summary>Motivo</summary>
              ${result.reason}
            </details>
          `;
            fileDiv.appendChild(resultDiv);
          }
          resultsContainer.appendChild(fileDiv);
        }
        // Hide loading
        loadingContainer.style.display = "none";
      })
      .catch((error) => {
        console.error(error);
      });
  });

  addPromptButton.addEventListener("click", () => {
    const newInput = document.createElement("input");
    newInput.className = "prompt-input";
    newInput.type = "text";
    newInput.placeholder = "Digite aqui a nova pergunta";
    document.getElementById("prompts").appendChild(newInput);
  });
});
