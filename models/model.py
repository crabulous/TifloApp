import torch
from transformers import BlipProcessor, BlipForConditionalGeneration, GPT2LMHeadModel, GPT2Tokenizer
from PIL import Image
import random
import logging
import asyncio
import re
import nltk
from nltk.corpus import stopwords
from googletrans import Translator

# Загружаем NLTK стоп-слова
nltk.download('stopwords')
stop_words = set(stopwords.words('english'))

# Инициализация переводчика
translator = Translator()

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация модели и процессора для генерации описаний
processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")

# Инициализация модели и токенизатора для перефразирования
gpt_tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
gpt_model = GPT2LMHeadModel.from_pretrained("gpt2")

# Константы для настройки параметров генерации описаний
TEMPERATURE_MIN = 0.7
TEMPERATURE_MAX = 0.8 #1.3
TOP_K_MIN = 30
TOP_K_MAX = 50 #100
TOP_P_MIN = 0.8
TOP_P_MAX = 0.85 #1.0


async def generate_single_caption(image_path, temperature=0.7, top_k=30, top_p=0.8):
    image = Image.open(image_path)
    inputs = processor(image, return_tensors="pt")
    out = model.generate(
        **inputs,
        max_length=128,
        do_sample=True,
        temperature=temperature,
        top_k=top_k,
        top_p=top_p,
        early_stopping=True
    )
    caption = processor.decode(out[0], skip_special_tokens=True)
    logging.info(f"Generated single caption: {caption}")
    return caption


async def generate_multiple_captions(image_path: str, num_captions: int):
    image = Image.open(image_path)
    inputs = processor(image, return_tensors="pt")
    tasks = [generate_single_caption(inputs,
                                     temperature=random.uniform(TEMPERATURE_MIN, TEMPERATURE_MAX),
                                     top_k=random.randint(TOP_K_MIN, TOP_K_MAX),
                                     top_p=random.uniform(TOP_P_MIN, TOP_P_MAX)) for _ in range(num_captions)]
    captions = await asyncio.gather(*tasks)
    logging.info(f"All generated captions: {captions}")
    return captions


def remove_duplicates(text: str) -> str:
    words = text.split()
    seen = set()
    result = []
    for word in words:
        if word.lower() not in seen:
            seen.add(word.lower())
            result.append(word)
    return ' '.join(result)


def remove_redundant_phrases(text: str) -> str:
    phrases = text.split(', ')
    filtered_phrases = []
    seen_phrases = set()
    for phrase in phrases:
        if phrase not in seen_phrases:
            seen_phrases.add(phrase)
            filtered_phrases.append(phrase)
    return ', '.join(filtered_phrases)


async def generate_caption(image_path: str):
    logging.info(f"Generating caption for image: {image_path}")
    caption = await generate_single_caption(image_path)
    # # Объединение всех описаний в одно предложение
    # combined_caption = ' '.join(captions)
    # logging.info(f"Combined caption: {combined_caption}")
    #
    # # Перефразирование финального описания с помощью GPT-2
    # final_caption = await paraphrase_caption(combined_caption)
    # logging.info(f"Final caption after paraphrasing: {final_caption}")
    #
    # # Удаление дубликатов и тавтологий
    # final_caption = remove_duplicates(final_caption)
    # final_caption = remove_redundant_phrases(final_caption)
    # logging.info(f"Final caption after removing duplicates and redundancies: {final_caption}")

    # Перевод на русский язык
    translated_caption = translate_to_russian(caption)
    logging.info(f"Translated caption: {translated_caption}")

    return translated_caption


async def paraphrase_caption(caption: str):
    inputs = gpt_tokenizer.encode(f"Paraphrase this: {caption}", return_tensors='pt')
    outputs = gpt_model.generate(
        inputs,
        max_length=150,
        num_return_sequences=1,
        do_sample=True,
        top_k=50,  # Слегка увеличиваем top_k
        top_p=0.7  # Слегка увеличиваем top_p
    )
    paraphrased_caption = gpt_tokenizer.decode(outputs[0], skip_special_tokens=True)
    return paraphrased_caption.replace("Paraphrase this:", "").strip()


def translate_to_russian(text: str) -> str:
    translated = translator.translate(text, src='en', dest='ru')
    return translated.text
