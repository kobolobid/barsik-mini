import re

P = "/root/zroute_bot/bot.py"
URL = "https://kobolobid.github.io/barsik-mini/tank/index.html"

s = open(P, encoding="utf-8").read()
orig = s
open(P + ".bak_tank", "w", encoding="utf-8").write(orig)
log = []

# 1. TANK_APP_URL
if "TANK_APP_URL" not in s:
    ins = 'TANK_APP_URL = os.environ.get("TANK_APP_URL", "' + URL + '")\n'
    for anchor in ["WINAMP_APP_URL =", "GAMES_APP_URL =", "CASINO_APP_URL =", "TAMA_APP_URL =", "GAME2048_APP_URL =", "MINI_APP_URL =", "BOT_TOKEN ="]:
        if anchor in s:
            s = s.replace(anchor, ins + anchor, 1)
            log.append("url")
            break

# 2. Import WebAppInfo
if "WebAppInfo" not in s:
    marker = "from aiogram.filters import CommandStart, Command"
    if marker in s:
        s = s.replace(marker, marker + "\nfrom aiogram.types import WebAppInfo", 1)
        log.append("import")

# 3. Command /tankapp
if "cmd_tankapp" not in s:
    cmd = (
        '@dp.message(Command("tankapp", "battlecity"))\n'
        'async def cmd_tankapp(message: Message):\n'
        '    url = globals().get("TANK_APP_URL") or os.environ.get("TANK_APP_URL", "' + URL + '")\n'
        '    if not url:\n'
        '        await message.answer("⚠️ TANK_APP_URL не задан.")\n'
        '        return\n'
        '    kb = InlineKeyboardMarkup(inline_keyboard=[[\n'
        '        InlineKeyboardButton(text="🎮 Играть в Танчики", web_app=WebAppInfo(url=url))\n'
        '    ]])\n'
        '    await message.answer("🎮 Нажми кнопку, чтобы открыть Battle City.", reply_markup=kb)\n'
        '\n\n'
    )
    marker = "@dp.message(CommandStart())"
    if marker in s:
        s = s.replace(marker, cmd + marker, 1)
        log.append("cmd")

# 4. Handle sendData from tank
if "tank_mini_save" not in s:
    web = (
        '@dp.message(F.web_app_data)\n'
        'async def tank_mini_save(message: Message):\n'
        '    if not message.web_app_data:\n'
        '        return None\n'
        '    try:\n'
        '        import json\n'
        '        data = json.loads(message.web_app_data.data or "{}")\n'
        '    except Exception:\n'
        '        return None\n'
        '    game = str(data.get("game", "")).lower()\n'
        '    if game != "tank":\n'
        '        return None\n'
        '    lvl = int(data.get("level") or 1)\n'
        '    sc = int(data.get("score") or 0)\n'
        '    await message.answer(f"🎮 Танчики: Уровень {lvl}, Очки {sc}.")\n'
        '    return None\n'
        '\n\n'
    )
    m = re.search(r"@dp\.message\(F\.web_app_data\)", s)
    if m:
        s = s[:m.start()] + web + s[m.start():]
        log.append("web_insert_before_existing")
    else:
        marker = "@dp.message(CommandStart())"
        if marker in s:
            s = s.replace(marker, web + marker, 1)
            log.append("web")

# 5. Add to /start menu
new_text = "🎮 Танчики — /tankapp (Mini App)"
lines = s.splitlines(True)
out = []
done = False
for line in lines:
    out.append(line)
    if not done and ("Казино" in line and "/casino" in line) or ("Плеер" in line and "/winampapp" in line):
        indent = line[:len(line) - len(line.lstrip())]
        out.append(indent + '"' + new_text + '\\n"\n')
        done = True

if done:
    s = "".join(out)
    log.append("start_line")

if s != orig:
    open(P, "w", encoding="utf-8").write(s)
    print("PATCH_TANK_OK:", log)
else:
    print("PATCH_TANK_NOCHANGES:", log)
