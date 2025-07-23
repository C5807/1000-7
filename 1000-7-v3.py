import random
import pyperclip
import keyboard
import time
import os
import sys
import tempfile
import atexit
import psutil  # Для проверки жив ли процесс
import threading
from msgs import boyfirst, boysec

# Путь к lock-файлу для предотвращения запуска нескольких копий
lock_file = os.path.join(tempfile.gettempdir(), '1000-7.lock')

# Глобальный флаг состояния цикла отправки
running = False
thread = None

def is_process_running(pid):
    """
    Проверяет, запущен ли процесс с указанным PID.
    """
    try:
        p = psutil.Process(pid)
        return p.is_running() and p.status() != psutil.STATUS_ZOMBIE
    except Exception:
        return False

def check_lock():
    """
    Проверяет наличие lock-файла.
    Если файл существует, проверяет, жив ли процесс, указанный в нем.
    Если процесс не жив, удаляет lock-файл.
    Если жив - завершает программу.
    """
    if os.path.exists(lock_file):
        try:
            with open(lock_file, 'r') as f:
                pid = int(f.read())
            if is_process_running(pid):
                print(f"Программа уже запущена (PID={pid})")
                sys.exit(0)
            else:
                print(f"Обнаружен битый lock-файл с PID={pid}, удаляю...")
                os.remove(lock_file)
        except Exception:
            print("Ошибка при проверке lock-файла, удаляю...")
            os.remove(lock_file)

    with open(lock_file, 'w') as f:
        f.write(str(os.getpid()))

    # Удаляем lock-файл при нормальном завершении скрипта
    atexit.register(lambda: os.remove(lock_file) if os.path.exists(lock_file) else None)

check_lock()

def send_message(text):
    """
    Отправляет текстовое сообщение в активное окно:
    - копирует текст в буфер обмена
    - открывает чат (Enter)
    - вставляет текст (Ctrl+V)
    - отправляет сообщение (Enter)
    """
    pyperclip.copy(text)
    keyboard.press_and_release('enter')
    time.sleep(0.05)
    keyboard.press_and_release('ctrl+v')
    time.sleep(0.03)
    keyboard.press_and_release('enter')
    time.sleep(0.3)

def spam_countdown():
    """
    Цикл отправки сообщений с выражениями вида 1000-7=993, 993-7=986 и т.д.
    Работает пока не остановлен флагом running или не дойдет до 0.
    """
    global running
    current = 1000
    running = True
    while running and current > 0:
        next_val = current - 7
        msg = f"{current}-7={next_val}"
        send_message(msg)
        current = next_val
    running = False
    print("[*] Цикл 1000-7 завершён или остановлен.")

def spam_insults(count=10):
    """
    Отправляет count сообщений с ругательствами,
    каждое сообщение — случайное сочетание из boyfirst + boysec
    """
    for _ in range(count):
        insult = f"{random.choice(boyfirst)} {random.choice(boysec)}"
        send_message(insult)

def start_countdown():
    """
    Запускает цикл 1000-7 в отдельном потоке, если он не запущен
    """
    global running, thread
    if not running:
        thread = threading.Thread(target=spam_countdown, daemon=True)
        thread.start()
        print("[+] Старт цикла 1000-7")

def stop_countdown():
    """
    Останавливает цикл 1000-7, выставляя флаг running в False
    """
    global running
    if running:
        running = False
        print("[-] Остановлено")

# Привязываем горячие клавиши
keyboard.add_hotkey('F8', start_countdown)         # Запуск цикла
keyboard.add_hotkey('F9', stop_countdown)          # Остановка цикла
keyboard.add_hotkey('right alt', lambda: spam_insults(10))  # 10 ругательств по правому Alt

print("F8 — старт 1000-7, F9 — стоп, Right Alt — 10 ругательств. Закрой окно для выхода.")

# Ожидаем событий клавиатуры (работает бесконечно)
keyboard.wait()
