document.getElementById('uploadForm').addEventListener('submit', async function(event) {
    event.preventDefault();
    const input = document.getElementById('fileInput');
    const formData = new FormData();
    formData.append('file', input.files[0]);

    const response = await fetch('/upload/', {
        method: 'POST',
        body: formData,
    });

    const result = await response.json();
    const resultDiv = document.getElementById('result');
    resultDiv.innerHTML = `<p>Filename: ${result.filename}</p><p>Caption: ${result.caption}</p>`;

    // Перезагрузка галереи
    window.location.reload();
});
