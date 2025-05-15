document.addEventListener('DOMContentLoaded', function() {
    const uploadForm = document.getElementById('uploadForm');
    const fileInput = document.getElementById('fileInput');
    const fileLabel = document.getElementById('fileLabel');
    const loadingText = document.getElementById('loadingText');
    const errorText = document.getElementById('errorText');

    loadingText.style.display = 'none';
    errorText.style.display = 'none';

    uploadForm.addEventListener('submit', async function(event) {
        event.preventDefault();

        if (fileInput.files.length === 0 || !isValidFileType(fileInput.files[0])) {
            errorText.style.display = 'block';
            return;
        }

        errorText.style.display = 'none';
        loadingText.style.display = 'block';

        try {
            const formData = new FormData(uploadForm);
            const response = await fetch(uploadForm.action, {
                method: 'POST',
                body: formData
            });

            if (response.ok) {
                window.location.reload();
            } else {
                throw new Error('Ошибка сервера');
            }
        } catch (error) {
            errorText.textContent = 'Ошибка при загрузке файла';
            errorText.style.display = 'block';
        } finally {
            loadingText.style.display = 'none';
            uploadForm.reset();
            fileLabel.textContent = 'Выбрать файл';
        }
    });

    function isValidFileType(file) {
        const validExtensions = ['.jpg', '.jpeg', '.png', '.svg'];
        const extension = '.' + file.name.split('.').pop().toLowerCase();
        return validExtensions.includes(extension);
    }
});
