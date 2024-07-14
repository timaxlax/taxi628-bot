 # Используем базовый образ Python
FROM python:3.9-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы requirements.txt и .env в рабочую директорию
COPY requirements.txt ./
COPY .env ./

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем все файлы проекта в рабочую директорию
COPY . .

# Команда для запуска бота
CMD ["python", "-m", "bot.main"]
