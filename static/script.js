<script>
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
    const filename = result.filename;

    // Проверяем, загрузилось ли изображение на сервер
    const img = new Image();
    img.onload = function () {
        // Если изображение загрузилось — обновляем страницу
        window.location.reload();
    };
    img.onerror = function () {
        // Если не удалось загрузить — выводим ошибку
        const errorText = document.getElementById('errorText');
        errorText.innerText = 'Ошибка при загрузке изображения.';
        errorText.style.display = 'block';
    };

    // Пробуем загрузить изображение (добавляем метку времени, чтобы избежать кэша)
    img.src = `/static/processed/${filename}?t=${Date.now()}`;
});
</script>
