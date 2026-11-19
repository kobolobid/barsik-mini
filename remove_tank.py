import re

P = "/root/zroute_bot/bot.py"
s = open(P, encoding="utf-8").read()
orig = s
log = []

# 1. Удаляем константу TANK_APP_URL
if "TANK_APP_URL" in s:
    # Ищем строку определения и удаляем её вместе с переносом строки
    pattern_url = r'TANK_APP_URL\s*=\s*[^\n]*\n'
    s = re.sub(pattern_url, '', s)
    log.append("removed_url")

# 2. Удаляем обработчик команды /tankapp
if "cmd_tankapp" in s:
    # Ищем декоратор @dp.message(Command("tankapp"...)) и функцию async def cmd_tankapp...
    # Паттерн захватывает весь блок функции до следующей пустой строки или следующего декоратора/комментария
    # Это грубый, но эффективный способ для простых функций
    
    # Вариант А: Если функция одна и та же структура
    pattern_cmd = r'@dp\.message\(Command\(["\']tankapp["\'],?\s*[^)]*\)\nasync def cmd_tankapp\(.*?\)(?:\n.*)*?(?=\n\n|\n@|\n#|$)'
    
    # Попробуем более безопасный подход: найти начало и конец блока
    start_marker = '@dp.message(Command("tankapp"'
    if start_marker in s:
        idx_start = s.find(start_marker)
        # Ищем следующую функцию или разделитель после этой
        # Простой поиск двойного перевода строки \n\n часто разделяет хендлеры
        next_double_newline = s.find('\n\n', idx_start)
        
        if next_double_newline != -1:
            # Проверяем, что между ними нет другого @dp.message
            block = s[idx_start:next_double_newline]
            if "@dp.message" not in block[len(start_marker):]: 
                s = s[:idx_start] + s[next_double_newline:]
                log.append("removed_handler_simple")
            else:
                log.append("handler_block_complex_skip")
        else:
             log.append("no_separator_found")
    else:
        log.append("marker_not_found")

# 3. Удаляем строку из /start
lines = s.splitlines(True)
out = []
for line in lines:
    # Пропускаем линии, содержащие ссылку на танчики в меню старта
    if "Танчики" in line and ("/tankapp" in line or "battle_city" in line.lower()):
        continue
    out.append(line)

if len(out) < len(lines):
    s = "".join(out)
    log.append("cleaned_start_menu")

if s != orig:
    open(P, "w", encoding="utf-8").write(s)
    print("REMOVE_TANK_OK:", log)
else:
    print("REMOVE_TANK_NOCHANGES:", log)
