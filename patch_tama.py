import re

P = "/root/zroute_bot/bot.py"
URL = "https://kobolobid.github.io/barsik-mini/tama/index.html"

s = open(P, encoding="utf-8").read()
orig = s
log = []

# 1. TAMA_APP_URL
if "TAMA_APP_URL" not in s:
    ins = 'TAMA_APP_URL = os.environ.get("TAMA_APP_URL", "' + URL + '")\n'
    for anchor in ["GAME2048_APP_URL =", "MINI_APP_URL =", "BOT_TOKEN ="]:
        if anchor in s:
            s = s.replace(anchor, ins + anchor, 1)
            log.append("url")
            break

# 2. WebAppInfo import
if "WebAppInfo" not in s:
    m = "from aiogram.filters import CommandStart, Command"
    if m in s:
        s = s.replace(m, m + "\nfrom aiogram.types import WebAppInfo", 1)
        log.append("import")

# 3. Команда /tamaapp
if "cmd_tamaapp" not in s:
    cmd = (
        '@dp.message(Command("tamaapp", "tamamini", "tama_app"))\n'
        'async def cmd_tamaapp(message: Message):\n'
        '    url = globals().get("TAMA_APP_URL") or os.environ.get("TAMA_APP_URL", "")\n'
        '    if not url:\n'
        '        await send_safe(message.chat.id, "⚠️ TAMA_APP_URL не задан.", message.message_thread_id)\n'
        '        return\n'
        '    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🐾 Играть в Тамагочи", web_app=WebAppInfo(url=url))]])\n'
        '    await send_safe(message.chat.id, "🐾 Нажми кнопку, чтобы открыть тамагочи.", message.message_thread_id, kb)\n'
        '\n\n'
    )
    a = "@dp.message(CommandStart())"
    if a in s:
        s = s.replace(a, cmd + a, 1)
        log.append("cmd")

# 4. Приём сохранения от Mini App (отдельный handler, не трогает существующие)
if "tama_mini_save" not in s:
    saver = (
        '@dp.message(F.web_app_data)\n'
        'async def tama_mini_save(message: Message):\n'
        '    if not message.web_app_data:\n'
        '        return None\n'
        '    try:\n'
        '        data = json.loads(message.web_app_data.data or "{}")\n'
        '    except Exception:\n'
        '        return None\n'
        '    if str(data.get("game", "")).lower() != "tama":\n'
        '        return None\n'
        '    st = data.get("state") or {}\n'
        '    uid = message.from_user.id if message.from_user else 0\n'
        '    name = message.from_user.first_name if message.from_user else "Игрок"\n'
        '    lv = int(data.get("level") or st.get("level") or 1)\n'
        '    cn = int(data.get("coins") or st.get("coins") or 0)\n'
        '    hh = int(float(data.get("happiness") or st.get("happiness") or 0))\n'
        '    hp = int(float(data.get("health") or st.get("health") or 0))\n'
        '    hg = int(float(data.get("hunger") or st.get("hunger") or 0))\n'
        '    pp = int(st.get("poop") or 0)\n'
        '    dj = json.dumps(st, ensure_ascii=False)[:60000]\n'
        '    try:\n'
        '        with sqlite3.connect(DB_PATH) as conn:\n'
        '            conn.execute("CREATE TABLE IF NOT EXISTS tama_mini(user_id INTEGER PRIMARY KEY,name TEXT,level INTEGER,coins INTEGER,happiness INTEGER,health INTEGER,hunger INTEGER,poop INTEGER,state TEXT,updated DATETIME DEFAULT CURRENT_TIMESTAMP)")\n'
        '            conn.execute("INSERT OR REPLACE INTO tama_mini(user_id,name,level,coins,happiness,health,hunger,poop,state,updated) VALUES(?,?,?,?,?,?,?,?,?,CURRENT_TIMESTAMP)", (uid, name, lv, cn, hh, hp, hg, pp, dj))\n'
        '    except Exception as e:\n'
        '        logging.error("tama mini save: %s", e)\n'
        '    await send_safe(message.chat.id, "🐾 Тамагочи сохранён: ⭐" + str(lv) + " 🪙" + str(cn) + " ❤️" + str(hp) + "% 🍖" + str(hg) + "% 💩" + str(pp), message.message_thread_id)\n'
        '    return None\n'
        '\n\n'
    )
    m1 = re.search(r"@dp\.message\(F\.web_app_data\)", s)
    if m1:
        s = s[:m1.start()] + saver + s[m1.start():]
        log.append("saver")
    else:
        a = "@dp.message(CommandStart())"
        if a in s:
            s = s.replace(a, saver + a, 1)
            log.append("saver2")

# 5. Строка в /start
if "/tamaapp (Mini App)" not in s:
    new_line = '   🐾 Тамагочи — /tamaapp (Mini App) или /tama (бот)'
    lines = s.splitlines(True)
    out = []
    done = False
    for line in lines:
        core = line.rstrip("\r\n")
        if not done and "Тамагочи" in core and "/tama" in core and "/tamaapp" not in core:
            indent = core[:len(core) - len(core.lstrip())]
            out.append(indent + '"' + new_line + '\\n"\n')
            done = True
        else:
            out.append(line)
    if done:
        s = "".join(out)
        log.append("start")

if s != orig:
    open(P, "w", encoding="utf-8").write(s)
    print("OK:", log)
else:
    print("NOCHANGES")
