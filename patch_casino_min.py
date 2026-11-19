import re

P = "/root/zroute_bot/bot.py"
URL = "https://kobolobid.github.io/barsik-mini/casino/index.html"

s = open(P, encoding="utf-8").read()
orig = s

open(P + ".bak_casino_min", "w", encoding="utf-8").write(orig)

log = []

if "import os" not in s:
    s = "import os\n" + s
    log.append("os")

if "WebAppInfo" not in s:
    lines = s.split("\n")
    for i, line in enumerate(lines):
        if line.startswith("from aiogram"):
            lines.insert(
                i + 1,
                "from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo"
            )
            log.append("types_import")
            break
    s = "\n".join(lines)

if "CASINO_APP_URL" not in s:
    ins = 'CASINO_APP_URL = os.environ.get("CASINO_APP_URL", "' + URL + '")\n'

    for anchor in [
        "TAMA_APP_URL =",
        "GAME2048_APP_URL =",
        "MINI_APP_URL =",
        "BOT_TOKEN =",
    ]:
        if anchor in s:
            s = s.replace(anchor, ins + anchor, 1)
            log.append("url")
            break

if "cmd_casinoapp" not in s:
    cmd = (
        '@dp.message(Command("casinoapp", "casino_mini", "kasinoapp"))\n'
        'async def cmd_casinoapp(message: Message):\n'
        '    url = globals().get("CASINO_APP_URL") or os.environ.get("CASINO_APP_URL", "' + URL + '")\n'
        '    if not url:\n'
        '        await message.answer("⚠️ CASINO_APP_URL не задан.", message_thread_id=message.message_thread_id)\n'
        '        return\n'
        '    kb = InlineKeyboardMarkup(inline_keyboard=[[\n'
        '        InlineKeyboardButton(text="🎰 Играть в казино", web_app=WebAppInfo(url=url))\n'
        '    ]])\n'
        '    await message.answer("🎰 Нажми кнопку, чтобы открыть Barsik Casino.", reply_markup=kb, message_thread_id=message.message_thread_id)\n'
        '\n\n'
    )

    marker = "@dp.message(CommandStart())"
    if marker in s:
        s = s.replace(marker, cmd + marker, 1)
        log.append("cmd")

if s != orig:
    open(P, "w", encoding="utf-8").write(s)
    print("PATCH_MIN_OK:", log)
else:
    print("PATCH_MIN_NOCHANGES:", log)
