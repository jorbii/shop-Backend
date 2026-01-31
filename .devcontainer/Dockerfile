FROM python:3.11-slim

# Встановлюємо робочу директорію
WORKDIR /app/Shop

# Копіюємо requirements та встановлюємо залежності
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копіюємо весь код проєкту
COPY . .

# Команда для запуску (використовуємо 0.0.0.0 для Docker)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
