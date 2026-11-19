import re

P = "/root/zroute_bot/bot.py"
URL = "https://kobolobid.github.io/barsik-mini/winamp/index.html"

s = open(P, encoding="utf-8").read()
orig = s
open(P + ".bak_winamp", "w", encoding="utf-8").write(orig)
log = []

# 1. WINAMP_APP_URL
if "WINAMP_APP_URL" not in s:
    ins = 'WINAMP_APP_URL = os.environ.get("WINAMP_APP_URL", "' + URL + '")\n'
    for anchor in ["GAMES_APP_URL =", "CASINO_APP_URL =", "TAMA_APP_URL =", "GAME2048_APP_URL =", "MINI_APP_URL =", "BOT_TOKEN ="]:
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

# 3. Command /winampapp
if "cmd_winampapp" not in s:
    cmd = (
        '@dp.message(Command("winampapp", "musicapp", "playerapp"))\n'
        'async def cmd_winampapp(message: Message):\n'
        '    url = globals().get("WINAMP_APP_URL") or os.environ.get("WINAMP_APP_URL", "' + URL + '")\n'
        '    if not url:\n'
        '        await message.answer("⚠️ WINAMP_APP_URL не задан.")\n'
        '        return\n'
        '    kb = InlineKeyboardMarkup(inline_keyboard=[[\n'
        '        InlineKeyboardButton(text="🎵 Открыть Barsik Amp", web_app=WebAppInfo(url=url))\n'
        '    ]])\n'
        '    await message.answer("🎵 Нажми кнопку, чтобы открыть плеер.", reply_markup=kb)\n'
        '\n\n'
    )
    marker = "@dp.message(CommandStart())"
    if marker in s:
        s = s.replace(marker, cmd + marker, 1)
        log.append("cmd")

# 4. Handle sendData from winamp
if "winamp_mini_save" not in s:
    web = (
        '@dp.message(F.web_app_data)\n'
        'async def winamp_mini_save(message: Message):\n'
        '    if not message.web_app_data:\n'
        '        return None\n'
        '    try:\n'
        '        import json\n'
        '        data = json.loads(message.web_app_data.data or "{}")\n'
        '    except Exception:\n'
        '        return None\n'
        '    game = str(data.get("game", "")).lower()\n'
        '    if game != "winamp":\n'
        '        return None\n'
        '    track = data.get("currentTrack", "Unknown")\n'
        '    playing = "Играет" if data.get("isPlaying") else "Пауза"\n'
        '    await message.answer(f"🎵 Barsik Amp статус:\\nТреклист: {track}\\nСостояние: {playing}")\n'
        '    return None\n'
        '\n\n'
    )
    # Insert before existing web_app_data handler if present, otherwise before CommandStart
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
new_text = "🎵 Плеер — /winampapp (Mini App)"
lines = s.splitlines(True)
out = []
done = False
for line in lines:
    out.append(line)
    if not done and ("Казино" in line and "/casino" in line) or ("Мини-игры" in line and "/gameapp" in line):
        indent = line[:len(line) - len(line.lstrip())]
        out.append(indent + '"' + new_text + '\\n"\n')
        done = True

if done:
    s = "".join(out)
    log.append("start_line")

if s != orig:
    open(P, "w", encoding="utf-8").write(s)
    print("PATCH_WINAMP_OK:", log)
else:
    print("PATCH_WINAMP_NOCHANGES:", log)
