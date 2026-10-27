FROM python:3.12-slim
RUN apt-get update && apt-get install -y --no-install-recommends libsdl2-2.0-0 libsdl2-image-2.0-0 \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV SDL_VIDEODRIVER=dummy DB_PATH=/app/data/snow_maze.db PYTHONUNBUFFERED=1
RUN mkdir -p /app/data
CMD ["python", "bot.py"]
