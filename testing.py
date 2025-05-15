import torch
from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image
import logging
import os
import numpy as np

# Инициализация моделей и процессоров
processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")

# Тестовые данные (5 изображений с конями, 5 с водой, 5 с городом)
test_data = [
    {"image_path": "test/horses1.jpg", "class": "Horse"},
    {"image_path": "test/horses2.jpg", "class": "Horse"},
    {"image_path": "test/horses3.jpg", "class": "Horse"},
    {"image_path": "test/horses4.jpg", "class": "Horse"},
    {"image_path": "test/horses5.jpg", "class": "Horse"},
    {"image_path": "test/water1.jpg", "class": "Water"},
    {"image_path": "test/water2.jpg", "class": "Water"},
    {"image_path": "test/water3.jpg", "class": "Water"},
    {"image_path": "test/water4.jpg", "class": "Water"},
    {"image_path": "test/water5.jpg", "class": "Water"},
    {"image_path": "test/city1.jpg", "class": "City"},
    {"image_path": "test/city2.jpg", "class": "City"},
    {"image_path": "test/city3.jpg", "class": "City"},
    {"image_path": "test/city4.jpg", "class": "City"},
    {"image_path": "test/city5.jpg", "class": "City"},
]

# Параметры модели
temperature = 0.7
top_k = 30
top_p = 0.8

def generate_caption(image_path):
    image = Image.open(image_path)
    inputs = processor(image, return_tensors="pt")
    out = model.generate(
        **inputs,
        max_length=128,
        do_sample=True,
        temperature=temperature,
        top_k=top_k,
        top_p=top_p
    )
    generated_caption = processor.decode(out[0], skip_special_tokens=True)
    return generated_caption

# Генерация сгенерированных описаний для тестовых данных
generated_captions = []
for data in test_data:
    if os.path.isfile(data["image_path"]):
        generated_caption = generate_caption(data["image_path"])
        generated_captions.append({"generated_caption": generated_caption, "class": data["class"]})
    else:
        print(f"File not found: {data['image_path']}")

# Подготовка списков референсных и сгенерированных описаний для каждого класса
reference_captions_horse = [data for data in test_data if data["class"] == "Horse"]
generated_captions_horse = [data for data in generated_captions if data["class"] == "Horse"]

reference_captions_water = [data for data in test_data if data["class"] == "Water"]
generated_captions_water = [data for data in generated_captions if data["class"] == "Water"]

reference_captions_city = [data for data in test_data if data["class"] == "City"]
generated_captions_city = [data for data in generated_captions if data["class"] == "City"]

# Функция для вычисления матрицы ошибок
def calculate_confusion_matrix(reference_captions, generated_captions, keyword):
    correct = 0
    incorrect = 0

    for ref, gen in zip(reference_captions, generated_captions):
        if keyword.lower() in gen["generated_caption"].lower():
            correct += 1
        else:
            incorrect += 1

    return np.array([[correct, incorrect]])

# Вычисление матриц ошибок для каждого класса
confusion_matrix_horse = calculate_confusion_matrix(reference_captions_horse, generated_captions_horse, "Horse")
confusion_matrix_water = calculate_confusion_matrix(reference_captions_water, generated_captions_water, "Water")
confusion_matrix_city = calculate_confusion_matrix(reference_captions_city, generated_captions_city, "City")

# Вывод матриц ошибок
print("Confusion Matrix - Horse:")
print(confusion_matrix_horse)
print("Confusion Matrix - Water:")
print(confusion_matrix_water)
print("Confusion Matrix - City:")
print(confusion_matrix_city)
