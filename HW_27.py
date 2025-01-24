import asyncio
from openai import AsyncOpenAI
from hw_27_data import DATA


API_KEY = "skszdxcrftgvbhjnimkol"
BASE_URL = "https://api.vsegpt.ru/v1"
MAX_CHUNK_SIZE = 4200
SLEEP_TIME = 4
OUTPUT_FILE = "output.md"

PROMPT_THEME = """
Привет!

Определи общую тему текста. И постарайся максимально полно и точно описать её,
с использованием пунктов и подпунктов.

Не додумывай того, чего там небыло.
Исключи small talks.
"""

PROMPT_TIMESTAMPS = """
Привет!

Ты - ассистент по созданию таймкодов для видео.
Тебе будет предоставлен текст с таймкодами из видео.
Твоя задача - создать краткое описание каждого смыслового блока.
Ты не должен использовать полное цитирование. Создай краткое описание для блока.
Каждый блок должен начинаться с таймкода в формате чч:мм:сс.
Описание должно быть одним предложением, передающим суть начинающегося отрезка.
Игнорируй слишком короткие фрагменты или паузы.
Объединяй связанные по смыслу части в один большой блок.
Описания должны быть в стиле, как это обычно делают на youtube.



ВАЖНО.
СТРОГИЕ ПРАВИЛА:
1. Для видео длительностью:
   - до 30 минут: максимум 5 таймкодов
   - 30-60 минут: максимум 8 таймкодов
   - 1-2 часа: максимум 10 таймкодов
   - 2+ часа: максимум 15 таймкодов

2. Минимальный интервал между таймкодами:
   - для коротких видео (до 30 мин): 3-5 минут
   - для длинных видео: 10-15 минут

3. Объединяй близкие по смыслу темы в один таймкод

ВАЖНО: Если ты превысишь количество таймкодов - твой ответ будет отклонён!

В твоём ответе должны быть только таймкоды и описания.
Никаких других комментариев или пояснений.

КАК ПИСАТЬ?

Ты не пишешь описательные, длинные предложения. 
Вроде: "Пояснение адаптивного подхода к верстке на примере Visual Studio Code, где контент перестраивается в зависимости от размера экрана. "

Ты пишешь короткий, ёмкий вариант.
"Адаптивный подход к вёрстке. Пример в Visual Studio Code. Контент перестраивается в зависимости от размера экрана."
Или даже ещё немного короче.

Спасибо!
"""

PROMPT_CONSPECT_WRITER = """
Привет!
Ты опытный технический писатель. Ниже, я предоставляю тебе полный текст лекции а так же ту часть,
с которой ты будешь работать.

Ты великолепно знаешь русский язык и отлично владеешь этой темой.

Тема занятия: {topic}

Полный текст лекции:
{full_text}

Сейчас я дам тебе ту часть, с котороый ты будешь работать. Я попрошу тебя написать конспект лекции.
А так же блоки кода.

Ты пишешь в формате Markdown. Начни с заголовка 2го уровня.
В тексте используй заголовки 3го уровня.

Используй блоки кода по необходимости.

Отрезок текста с которым ты работаешь, с которого ты будешь работать:
{text_to_work}
"""
client = AsyncOpenAI(api_key=API_KEY, base_url=BASE_URL)

async def get_ai_request(chunk, topic="Автоматически сгенерированный конспект"):
    try:
        formatted_prompt = PROMPT_CONSPECT_WRITER.format(
            topic=topic, full_text=full_text_global, text_to_work=chunk
        )  # Используем глобальную переменную
        response = await client.chat.completions.create(
            model="openai/gpt-4o-mini",
            messages=[{"role": "user", "content": formatted_prompt}],
            max_tokens=150,
            temperature=0.7,
        )
        await asyncio.sleep(SLEEP_TIME)
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Ошибка: {e}")
        return f"Ошибка обработки блока: {e}"


def split_text(text):
    return [text[i : i + MAX_CHUNK_SIZE] for i in range(0, len(text), MAX_CHUNK_SIZE)]


async def generate_timestamps(text, topic="Автоматически сгенерированный конспект"):
    try:
        formatted_prompt = PROMPT_TIMESTAMPS.format(topic=topic, full_text=text)
        response = await client.chat.completions.create(
            model="openai/gpt-4o-mini",
            messages=[{"role": "user", "content": formatted_prompt}],
            max_tokens=500,
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Ошибка: {e}")
        return f"Ошибка генерации таймкодов: {e}"


async def save_to_markdown(timestamps, conspect_chunks):
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(timestamps + "\n\n---\n\n")
        f.write("## Конспект занятия\n\n")
        for chunk in conspect_chunks:
            f.write(chunk + "\n\n")


async def main():
    global full_text_global  # Объявляем full_text_global как глобальную
    full_text_global = ""
    for item in DATA:
        full_text_global += item["text"]

    timestamps_output = await generate_timestamps(full_text_global)
    chunks = split_text(full_text_global)
    tasks = [get_ai_request(chunk) for chunk in chunks]
    conspect_chunks = await asyncio.gather(*tasks)

    await save_to_markdown(timestamps_output, conspect_chunks)
    print(f"Результаты сохранены в {OUTPUT_FILE}")


if __name__ == "__main__":
    asyncio.run(main())