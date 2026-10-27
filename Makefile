VENV := .venv
PY   := $(VENV)/bin/python3
PIP  := $(VENV)/bin/pip
.PHONY: help install install-dev test run bot docker-build docker-run clean
help:
	@echo "install / install-dev / test / run / bot / docker-build / docker-run"
$(VENV):
	python3 -m venv $(VENV)
install: $(VENV)
	$(PIP) install --upgrade pip && $(PIP) install -e .
install-dev: $(VENV)
	$(PIP) install --upgrade pip && $(PIP) install -e ".[dev]"
test: $(VENV)
	SDL_VIDEODRIVER=dummy $(PY) -m pytest -v
run: $(VENV)
	$(PY) main.py
bot: $(VENV)
	$(PY) bot.py
docker-build:
	docker build -t snow-maze-bot .
docker-run:
	mkdir -p data && docker run --rm --env-file .env -v "$$(pwd)/data:/app/data" snow-maze-bot
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	rm -rf build/ dist/
