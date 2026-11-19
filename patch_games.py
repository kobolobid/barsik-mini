import re

P = "/root/zroute_bot/bot.py"
URL = "https://kobolobid.github.io/barsik-mini/games/index.html?v=4"

s = open(P, encoding="utf-8").read()
orig = s

open(P + ".bak_games", "w", encoding="utf-8").write(orig)

log = []

# ---------------------------------------------------------------
# 1. GAMES_APP_URL
# ---------------------------------------------------------------
if "GAMES_APP_URL" not in s:
    ins = 'GAMES_APP_URL = os.environ.get("GAMES_APP_URL", "' + URL + '")\n'

    for anchor in [
        "CASINO_APP_URL =",
        "TAMA_APP_URL =",
        "GAME2048_APP_URL =",
        "MINI_APP_URL =",
        "BOT_TOKEN =",
    ]:
        if anchor in s:
            s = s.replace(anchor, ins + anchor, 1)
            log.append("url")
            break

# ---------------------------------------------------------------
# 2. WebAppInfo import
# ---------------------------------------------------------------
if "WebAppInfo" not in s:
    marker = "from aiogram.filters import CommandStart, Command"
    if marker in s:
        s = s.replace(
            marker,
            marker + "\nfrom aiogram.types import WebAppInfo",
            1
        )
        log.append("import_webapp")

# ---------------------------------------------------------------
# 3. Команда /gameapp
# ---------------------------------------------------------------
if "cmd_gameapp" not in s:
    cmd = (
        '@dp.message(Command("gameapp", "gamesapp", "mini_games", "games_mini"))\n'
        'async def cmd_gameapp(message: Message):\n'
        '    url = globals().get("GAMES_APP_URL") or os.environ.get("GAMES_APP_URL", "' + URL + '")\n'
        '    if not url:\n'
        '        await message.answer("⚠️ GAMES_APP_URL не задан.")\n'
        '        return\n'
        '    kb = InlineKeyboardMarkup(inline_keyboard=[[\n'
        '        InlineKeyboardButton(text="🎯 Играть в мини-игры", web_app=WebAppInfo(url=url))\n'
        '    ]])\n'
        '    await message.answer("🎯 Нажми кнопку, чтобы открыть Barsik Mini Games.", reply_markup=kb)\n'
        '\n\n'
    )

    marker = "@dp.message(CommandStart())"
    if marker in s:
        s = s.replace(marker, cmd + marker, 1)
        log.append("cmd")

# ---------------------------------------------------------------
# 4. Приём сохранения из Mini App games
# ---------------------------------------------------------------
if "games_mini_save" not in s:
    web = (
        '@dp.message(F.web_app_data)\n'
        'async def games_mini_save(message: Message):\n'
        '    if not message.web_app_data:\n'
        '        return None\n'
        '    try:\n'
        '        import json\n'
        '        data = json.loads(message.web_app_data.data or "{}")\n'
        '    except Exception:\n'
        '        return None\n'
        '    game = str(data.get("game", "")).lower()\n'
        '    if game != "games":\n'
        '        return None\n'
        '    uid = message.from_user.id if message.from_user else 0\n'
        '    name = message.from_user.first_name if message.from_user else "Игрок"\n'
        '    balance = int(data.get("balance") or 0)\n'
        '    played = int(data.get("played") or 0)\n'
        '    won = int(data.get("won") or 0)\n'
        '    best = int(data.get("best") or 0)\n'
        '    try:\n'
        '        state_json = json.dumps(data.get("state") or data, ensure_ascii=False)[:60000]\n'
        '    except Exception:\n'
        '        state_json = "{}"\n'
        '    try:\n'
        '        import sqlite3\n'
        '        import os\n'
        '        db = globals().get("DB_PATH") or os.path.join(os.path.dirname(os.path.abspath(__file__)), "bot_users.db")\n'
        '        with sqlite3.connect(db) as conn:\n'
        '            conn.execute("CREATE TABLE IF NOT EXISTS games_mini(user_id INTEGER PRIMARY KEY,name TEXT,balance INTEGER,played INTEGER,won INTEGER,best INTEGER,state TEXT,updated DATETIME DEFAULT CURRENT_TIMESTAMP)")\n'
        '            conn.execute("INSERT OR REPLACE INTO games_mini(user_id,name,balance,played,won,best,state,updated) VALUES(?,?,?,?,?,?,?,CURRENT_TIMESTAMP)", (uid, name, balance, played, won, best, state_json))\n'
        '    except Exception:\n'
        '        pass\n'
        '    return await message.answer("🎯 Мини-игры сохранены: 🪙" + str(balance) + " · игр " + str(played) + " · побед " + str(won) + " · лучший выигрыш " + str(best))\n'
        '\n\n'
    )

    m = re.search(r"@dp\.message\(F\.web_app_data\)", s)
    if m:
        s = s[:m.start()] + web + s[m.start():]
        log.append("web_before_existing")
    else:
        marker = "@dp.message(CommandStart())"
        if marker in s:
            s = s.replace(marker, web + marker, 1)
            log.append("web")

# ---------------------------------------------------------------
# 5. Строка в /start
# ---------------------------------------------------------------
new_text = "🎯 Мини-игры — /gameapp (Mini App) или /game (бот)"

lines = s.splitlines(True)
out = []
done = False

for line in lines:
    if not done and "Мини-игры" in line and "/game" in line and "/gameapp" not in line:
        stripped = line.lstrip()
        indent = line[:len(line) - len(stripped)]

        if line.endswith("\r\n"):
            eol = "\r\n"
        elif line.endswith("\n"):
            eol = "\n"
        elif line.endswith("\r"):
            eol = "\r"
        else:
            eol = ""

        out.append(indent + '"' + new_text + '\\n"' + eol)
        done = True
    else:
        out.append(line)

if done:
    s = "".join(out)
    log.append("start")

if s != orig:
    open(P, "w", encoding="utf-8").write(s)
    print("PATCH_GAMES_OK:", log)
else:
    print("PATCH_GAMES_NOCHANGES:", log)
