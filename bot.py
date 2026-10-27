"""Telegram-обёртка. pygame через asyncio.Lock.

Фиксы v1.0.1:
- нажатие в стену (moved=False) не редактирует сообщение и не сбрасывает игру;
- "message is not modified" обрабатывается отдельно, без clear();
- ctx.bot вместо устаревшего update.get_bot().
"""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import asyncio
import logging
import time

from dotenv import load_dotenv

load_dotenv()  # ДО import db — DB_PATH применяется

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto, Update
from telegram.ext import (Application, CallbackQueryHandler, CommandHandler,
                          ContextTypes, MessageHandler, filters)

import db
from game import Game, should_record_loss

TOKEN = os.environ.get("BOT_TOKEN")
if not TOKEN or TOKEN == "здесь_будет_ваш_токен":
    raise SystemExit("BOT_TOKEN не задан\n  cp .env.example .env\n  nano .env")

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("bot")
db.init_db()
_pygame_lock = asyncio.Lock()


def controls():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⬆️", callback_data="move:up")],
        [InlineKeyboardButton("⬅️", callback_data="move:left"),
         InlineKeyboardButton("⬇️", callback_data="move:down"),
         InlineKeyboardButton("➡️", callback_data="move:right")],
        [InlineKeyboardButton("🔄 Новая игра", callback_data="new")],
    ])


async def _new_game_safe():
    async with _pygame_lock:
        return await asyncio.to_thread(Game)


async def _render_safe(g):
    async with _pygame_lock:
        return await asyncio.to_thread(g.render)


async def _maybe_record_loss(ctx, user):
    g = ctx.user_data.get("game")
    won = ctx.user_data.get("won_this_game", False)
    first = ctx.user_data.get("first_move_ts")
    if not should_record_loss(g, won, first):
        return
    elapsed = int((time.monotonic() - first) * 1000)
    try:
        uid = await asyncio.to_thread(db.get_or_create_user, user.id, user.username)
        await asyncio.to_thread(db.insert_game, uid, g.moves, elapsed, False)
    except Exception:
        log.exception("loss fail")


async def cmd_start(update, ctx):
    user = update.effective_user
    await _maybe_record_loss(ctx, user)
    prev = ctx.user_data.get("message_id")
    if prev:
        try:
            await ctx.bot.delete_message(update.effective_chat.id, prev)
        except Exception:
            pass
    ctx.user_data.clear()
    game = await _new_game_safe()
    ctx.user_data["game"] = game
    ctx.user_data["first_move_ts"] = None
    ctx.user_data["won_this_game"] = False
    png = await _render_safe(game)
    msg = await update.message.reply_photo(
        photo=png, caption="❄️ Snow Maze Runner\nУправление — кнопки ниже.",
        reply_markup=controls())
    ctx.user_data["message_id"] = msg.message_id


async def cmd_stats(update, ctx):
    user = update.effective_user
    try:
        await asyncio.to_thread(db.get_or_create_user, user.id, user.username)
        s = await asyncio.to_thread(db.get_user_stats, user.id)
    except Exception:
        log.exception("stats fail")
        await update.message.reply_text("Ошибка статистики.")
        return
    if not s or s.get("total_games", 0) == 0:
        await update.message.reply_text("Статистики нет. /start")
        return
    best = s["best_time_ms"]
    best_str = f"{best / 1000:.1f}s" if best else "—"
    await update.message.reply_text(
        f"📊 Игр: {s['total_games']}\nПобед: {s['wins']}\n"
        f"Среднее ходов: {s['avg_moves']:.1f}\nЛучшее время: {best_str}")


async def cmd_leaderboard(update, ctx):
    try:
        rows = await asyncio.to_thread(db.get_leaderboard, 10)
    except Exception:
        await update.message.reply_text("Ошибка лидерборда.")
        return
    if not rows:
        await update.message.reply_text("Лидерборд пуст. /start")
        return
    lines = ["🏆 Топ-10:"]
    for i, r in enumerate(rows, 1):
        lines.append(f"{i}. {r['username'] or 'аноним'} — {r['best_time'] / 1000:.1f}s, {r['wins']} побед")
    await update.message.reply_text("\n".join(lines))


async def cmd_help(update, ctx):
    await update.message.reply_text(
        "/start — игра\n/stats — статистика\n/leaderboard — топ-10\n"
        "Управление — кнопки под картинкой.")


async def on_button(update, ctx):
    q = update.callback_query
    await q.answer()
    user = q.from_user
    game = ctx.user_data.get("game")
    if not game:
        await q.message.reply_text("Игра не найдена. /start")
        return

    if q.data == "new":
        await _maybe_record_loss(ctx, user)
        game = await _new_game_safe()
        ctx.user_data["game"] = game
        ctx.user_data["first_move_ts"] = None
        ctx.user_data["won_this_game"] = False
    elif q.data.startswith("move:"):
        moved = game.move(q.data.split(":", 1)[1])
        if not moved:
            return  # ФИКС: нажали в стену — состояние не изменилось, ничего не делаем
        if ctx.user_data.get("first_move_ts") is None:
            ctx.user_data["first_move_ts"] = time.monotonic()

    won = game.is_won()
    if won and not ctx.user_data.get("won_this_game"):
        ctx.user_data["won_this_game"] = True
        first = ctx.user_data["first_move_ts"]
        elapsed = int((time.monotonic() - first) * 1000)
        try:
            uid = await asyncio.to_thread(db.get_or_create_user, user.id, user.username)
            await asyncio.to_thread(db.insert_game, uid, game.moves, elapsed, True)
        except Exception:
            log.exception("win fail")

    png = await _render_safe(game)
    caption = f"🎉 Победа! Ходов: {game.moves}" if won else "❄️ Snow Maze Runner"
    try:
        await q.edit_message_media(
            media=InputMediaPhoto(media=png, caption=caption),
            reply_markup=controls())
    except Exception as e:
        if "message is not modified" in str(e):
            return  # ФИКС: нечего менять — не ошибка, игру не трогаем
        log.exception("edit fail")
        ctx.user_data.clear()
        msg = await q.message.reply_text("Не удалось обновить. Нажмите /start")
        ctx.user_data["message_id"] = msg.message_id


async def on_text(update, ctx):
    await update.message.reply_text("Нажмите /start")


def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("stats", cmd_stats))
    app.add_handler(CommandHandler("leaderboard", cmd_leaderboard))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CallbackQueryHandler(on_button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_text))
    log.info("Bot started")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
