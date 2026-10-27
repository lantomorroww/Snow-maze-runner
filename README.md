# ❄️ Snow Maze Runner

[![CI](https://github.com/lantomorroww/snow-maze-runner/actions/workflows/ci.yml/badge.svg)](https://github.com/lantomorroww/snow-maze-runner/actions/workflows/ci.yml)

Лабиринт со снежной тематикой: генерируется случайно алгоритмом **DFS (recursive backtracker)**. Играть можно локально (pygame) или через **Telegram-бота** — управление inline-кнопками ⬆️⬇️⬅️➡️. Бот ведёт **SQLite-лидерборд** и статистику (`/stats`, `/leaderboard`), работает в **Docker**.

> Портфолио-проект: алгоритмы, pygame, асинхронный Telegram Bot API, SQLite (JOIN, GROUP BY, агрегаты), thread-safe headless-рендер, Docker, pytest + CI.

## ✨ Возможности

- 🎲 Генерация лабиринта DFS — связный, без изолированных комнат.
- 🖥️ Локальный режим (pygame) и 📱 Telegram-режим.
- 🧩 Общая логика в `maze.py` и `game.py`.
- 🗄️ SQLite: `users` + `games`, лидерборд (`JOIN` + `GROUP BY`), личная статистика (`AVG`, `SUM`, `MIN`), защита от SQL-инъекций через `?`.
- ⚡ `asyncio.to_thread` + `asyncio.Lock` — pygame не thread-safe, все `Game()` и `render()` сериализованы. Event loop не блокируется.
- 📉 Фиксация поражений — если игрок бросил игру после хотя бы одного хода, при следующем `/start` записывается loss. Без ходов — не считается партией (проверка в чистой `should_record_loss`).
- ⏱️ Честный таймер — `time_ms` от первого хода, бездействие не портит лидерборд.
- 🎯 UX-фикс: нажатие в стену не сбрасывает игру и не вызывает ошибку `message is not modified`.
- 🐳 Docker (`python:3.12-slim` + `libsdl2`, headless-safe).
- ✅ CI: Python 3.10/3.11/3.12, `py_compile`, `pytest`.

## 🏗️ Архитектура

1. `maze.py` — чистая логика генерации.
2. `game.py` — `Game` + чистая `should_record_loss()`. Headless-режим включается извне (`bot.py`, `tests/conftest.py` выставляют `SDL_VIDEODRIVER=dummy` до импорта). `main.py` открывает реальное окно.
3. `main.py` — локальная игра.
4. `bot.py` — Telegram: pygame через `_pygame_lock` + `asyncio.to_thread`.
5. `db.py` — SQLite (`closing` — соединения закрываются).

Почему `asyncio.Lock` вокруг pygame: `pygame` держит общее состояние SDL и не thread-safe. Без лока при 3+ нажатиях — краши и битые PNG.

Почему SQLite: `context.user_data` теряется при рестарте. Лидерборд живёт между рестартами.

## 🚀 Установка

    git clone git@github.com:lantomorroww/snow-maze-runner.git
    cd snow-maze-runner
    make install-dev
    make test

Локальная игра:

    make run

Telegram-бот:

    cp .env.example .env
    nano .env
    make bot

Docker:

    make docker-build && make docker-run

## 🧪 Тесты

`make test` — покрыто `maze`, `game`, `should_record_loss`, `db`. Всего 19 тестов, CI прогоняет на Python 3.10/3.11/3.12.

## 🖼️ Свои картинки

Положите `images/background_1.png` и `images/char.png`. Без них — цветные заглушки.

## 📄 Лицензия

[MIT](LICENSE) © 2026 Dmitry Budenkov

## 📌 Статус

Активно поддерживается.

- **2026-10 (v1.0.1)** — UX-фикс: нажатие в стену не сбрасывает игру; `message is not modified` обрабатывается отдельно; `ctx.bot` вместо устаревшего `update.get_bot()`.
- **2026-10 (v1.0.0)** — фиксация поражений, `asyncio.Lock`, честный таймер, SQLite, Docker, CI.
- **2026-09** — первая версия.
