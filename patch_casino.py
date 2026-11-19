import re

P = "/root/zroute_bot/bot.py"
URL = "https://kobolobid.github.io/barsik-mini/casino/index.html"

s = open(P, encoding="utf-8").read()
orig = s
log = []

open(P + ".bak_casino", "w", encoding="utf-8").write(orig)

# ---------------------------------------------------------------
# Импорты
# ---------------------------------------------------------------
if "WebAppInfo" not in s:
    marker = "from aiogram.filters import CommandStart, Command"
    if marker in s:
        s = s.replace(marker, marker + "\nfrom aiogram.types import WebAppInfo", 1)
        log.append("import_webapp")

if "\nimport json" not in s:
    marker = "import os"
    if marker in s:
        s = s.replace(marker, marker + "\nimport json", 1)
        log.append("import_json")

if "\nimport sqlite3" not in s:
    marker = "import os"
    if marker in s:
        s = s.replace(marker, marker + "\nimport sqlite3", 1)
        log.append("import_sqlite3")

# ---------------------------------------------------------------
# Константа CASINO_APP_URL
# ---------------------------------------------------------------
if "CASINO_APP_URL" not in s:
    ins = 'CASINO_APP_URL = os.environ.get("CASINO_APP_URL", "' + URL + '")\n'
    for anchor in ["TAMA_APP_URL =", "GAME2048_APP_URL =", "MINI_APP_URL =", "BOT_TOKEN ="]:
        if anchor in s:
            s = s.replace(anchor, ins + anchor, 1)
            log.append("url")
            break

# ---------------------------------------------------------------
# Команда /casinoapp
# ---------------------------------------------------------------
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

# ---------------------------------------------------------------
# Универсальный приём Mini App данных, включая casino
# ---------------------------------------------------------------
if "casino_mini" not in s:
    web = (
        '@dp.message(F.web_app_data)\n'
        'async def on_miniapp_data_universal(message: Message):\n'
        '    if not message.web_app_data:\n'
        '        return\n'
        '    try:\n'
        '        data = json.loads(message.web_app_data.data or "{}")\n'
        '    except Exception:\n'
        '        data = {}\n'
        '    game = str(data.get("game", "")).lower()\n'
        '    uid = message.from_user.id if message.from_user else 0\n'
        '    name = message.from_user.first_name if message.from_user else "Игрок"\n'
        '\n'
        '    if game == "casino":\n'
        '        balance = int(data.get("balance") or 0)\n'
        '        hands = int(data.get("hands") or 0)\n'
        '        wins = int(data.get("wins") or 0)\n'
        '        wagered = int(data.get("wagered") or 0)\n'
        '        best = int(data.get("best") or 0)\n'
        '        last_bonus = int(data.get("lastBonus") or 0)\n'
        '        last_help = int(data.get("lastHelp") or 0)\n'
        '        try:\n'
        '            state_json = json.dumps(data.get("state") or data, ensure_ascii=False)[:60000]\n'
        '        except Exception:\n'
        '            state_json = "{}"\n'
        '        try:\n'
        '            with sqlite3.connect(DB_PATH) as conn:\n'
        '                conn.execute("CREATE TABLE IF NOT EXISTS casino_mini(user_id INTEGER PRIMARY KEY,name TEXT,balance INTEGER,hands INTEGER,wins INTEGER,wagered INTEGER,best INTEGER,last_bonus INTEGER,last_help INTEGER,state TEXT,updated DATETIME DEFAULT CURRENT_TIMESTAMP)")\n'
        '                conn.execute("INSERT OR REPLACE INTO casino_mini(user_id,name,balance,hands,wins,wagered,best,last_bonus,last_help,state,updated) VALUES(?,?,?,?,?,?,?,?,?,?,CURRENT_TIMESTAMP)", (uid, name, balance, hands, wins, wagered, best, last_bonus, last_help, state_json))\n'
        '        except Exception as e:\n'
        '            logging.error("casino mini save: %s", e)\n'
        '        await message.answer("🎰 Казино сохранено: 🪙" + str(balance) + " · игр " + str(hands) + " · побед " + str(wins) + " · лучший выигрыш " + str(best), message_thread_id=message.message_thread_id)\n'
        '        return\n'
        '\n'
        '    if game == "tama":\n'
        '        st = data.get("state") or {}\n'
        '        lv = int(data.get("level") or st.get("level") or 1)\n'
        '        cn = int(data.get("coins") or st.get("coins") or 0)\n'
        '        hh = int(float(data.get("happiness") or st.get("happiness") or 0))\n'
        '        hp = int(float(data.get("health") or st.get("health") or 0))\n'
        '        hg = int(float(data.get("hunger") or st.get("hunger") or 0))\n'
        '        bl = int(float(st.get("belly") or 0))\n'
        '        pp = int(st.get("poop") or 0)\n'
        '        try:\n'
        '            state_json = json.dumps(st, ensure_ascii=False)[:60000]\n'
        '        except Exception:\n'
        '            state_json = "{}"\n'
        '        try:\n'
        '            with sqlite3.connect(DB_PATH) as conn:\n'
        '                conn.execute("CREATE TABLE IF NOT EXISTS tama_mini(user_id INTEGER PRIMARY KEY,name TEXT,level INTEGER,coins INTEGER,happiness INTEGER,health INTEGER,hunger INTEGER,belly INTEGER,poop INTEGER,state TEXT,updated DATETIME DEFAULT CURRENT_TIMESTAMP)")\n'
        '                conn.execute("INSERT OR REPLACE INTO tama_mini(user_id,name,level,coins,happiness,health,hunger,belly,poop,state,updated) VALUES(?,?,?,?,?,?,?,?,?,CURRENT_TIMESTAMP)", (uid, name, lv, cn, hh, hp, hg, bl, pp, state_json))\n'
        '        except Exception as e:\n'
        '            logging.error("tama mini save: %s", e)\n'
        '        await message.answer("🐾 Тамагочи сохранён: ⭐" + str(lv) + " 🪙" + str(cn) + " ❤️" + str(hp) + "% 🍖" + str(hg) + "% 🫃" + str(bl) + "% 💩" + str(pp), message_thread_id=message.message_thread_id)\n'
        '        return\n'
        '\n'
        '    if game == "2048":\n'
        '        score = int(data.get("score") or 0)\n'
        '        best = int(data.get("best") or 0)\n'
        '        moves = int(data.get("moves") or 0)\n'
        '        won = 1 if data.get("won") else 0\n'
        '        over = 1 if data.get("over") else 0\n'
        '        try:\n'
        '            with sqlite3.connect(DB_PATH) as conn:\n'
        '                conn.execute("CREATE TABLE IF NOT EXISTS scores2048(id INTEGER PRIMARY KEY AUTOINCREMENT,user_id INTEGER,name TEXT,score INTEGER,best INTEGER,moves INTEGER,won INTEGER,over INTEGER,created DATETIME DEFAULT CURRENT_TIMESTAMP)")\n'
        '                conn.execute("INSERT INTO scores2048(user_id,name,score,best,moves,won,over) VALUES(?,?,?,?,?,?,?)", (uid, name, score, best, moves, won, over))\n'
        '        except Exception as e:\n'
        '            logging.error("2048 score save: %s", e)\n'
        '        await message.answer("🎮 2048 сохранён: " + str(score) + " очков, " + str(moves) + " ходов, рекорд " + str(best), message_thread_id=message.message_thread_id)\n'
        '        return\n'
        '\n'
        '    score = int(data.get("score") or 0)\n'
        '    lines = int(data.get("lines") or 0)\n'
        '    level = int(data.get("level") or 1)\n'
        '    try:\n'
        '        with sqlite3.connect(DB_PATH) as conn:\n'
        '            conn.execute("CREATE TABLE IF NOT EXISTS tetris_scores(id INTEGER PRIMARY KEY AUTOINCREMENT,user_id INTEGER,name TEXT,score INTEGER,lines INTEGER,level INTEGER,created DATETIME DEFAULT CURRENT_TIMESTAMP)")\n'
        '            conn.execute("INSERT INTO tetris_scores(user_id,name,score,lines,level) VALUES(?,?,?,?,?)", (uid, name, score, lines, level))\n'
        '    except Exception as e:\n'
        '        logging.error("tetris score save: %s", e)\n'
        '    await message.answer("🎮 Tetris сохранён: " + str(score) + " очков, " + str(lines) + " линий, уровень " + str(level), message_thread_id=message.message_thread_id)\n'
        '\n\n'
    )

    m = re.search(r"@dp\.message\(F\.web_app_data\)", s)
    if m:
        s = s[:m.start()] + web + s[m.start():]
        log.append("web_before_old")
    else:
        marker = "@dp.message(CommandStart())"
        if marker in s:
            s = s.replace(marker, web + marker, 1)
            log.append("web")

# ---------------------------------------------------------------
# Строка в /start
# ---------------------------------------------------------------
new_start = "Казино — /casinoapp (Mini App) или /casino (бот)"

if new_start in s:
    log.append("start_already")
else:
    lines = s.splitlines(True)
    out = []
    done = False

    for line in lines:
        if not done and "Казино" in line and "/casino" in line and "/casinoapp" not in line:
            indent = line[:len(line) - len(line.lstrip())]
            if line.endswith("\r\n"):
                eol = "\r\n"
            elif line.endswith("\n"):
                eol = "\n"
            elif line.endswith("\r"):
                eol = "\r"
            else:
                eol = ""

            out.append(indent + '"   ' + new_start + '\\n"' + eol)
            done = True
        else:
            out.append(line)

    if done:
        s = "".join(out)
        log.append("start")

if s != orig:
    open(P, "w", encoding="utf-8").write(s)
    print("PATCH_CASINO_OK:", log)
else:
    print("PATCH_CASINO_NOCHANGES:", log)
