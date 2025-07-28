import os
import sys
import subprocess
from pathlib import Path

def get_venv_python():
    if os.name == "nt":
        return str(Path("venv") / "Scripts" / "python.exe")
    else:
        return str(Path("venv") / "bin" / "python")

def is_venv_active():
    return (
        hasattr(sys, 'real_prefix')
        or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    )

def ensure_package(package):
    try:
        __import__(package)
    except ImportError:
        print(f"Устанавливаю пакет '{package}'…")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

def setup_environment():
    venv_dir = Path("venv")

    if not is_venv_active():
        # 1. Создаём venv если нужно
        if not venv_dir.exists():
            print("[*] Виртуальное окружение не найдено. Создаём venv...")
            subprocess.check_call([sys.executable, "-m", "venv", "venv"])
            print("\n✅ Виртуальное окружение создано в ./venv\n")

        # 2. Перезапускаем себя из-под venv python
        venv_python = get_venv_python()
        if not Path(venv_python).exists():
            print(f"Ошибка: не найден venv python по пути {venv_python}")
            sys.exit(1)
        print("[*] Перезапуск скрипта внутри виртуального окружения...\n")
        subprocess.check_call([venv_python] + sys.argv)
        sys.exit(0)
        time.sleep(10)

    for pkg in ["eth_account", "mnemonic", "base58"]:
        ensure_package(pkg)

def try_import_bip_utils():
    try:
        from bip_utils import Bip39SeedGenerator, Bip44, Bip44Coins, Bip44Changes
        return True
    except ImportError:
        return False

import webbrowser

import time
import webbrowser

def install_bip_utils():
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "bip_utils"])
        print("\n✅ Модуль 'bip_utils' установлен! Запустите скрипт заново.")
        sys.exit(0)
    except Exception as e:
        print("\n❌ Не удалось установить 'bip_utils' автоматически.")

        if os.name == "nt":
            print(
                "\nНа Windows необходим Microsoft Visual C++ Build Tools!\n"
                "====================\n"
                "❶ Откроется страница загрузки Visual C++ Build Tools.\n"
                "❷ Скачайте и установите Build Tools for Visual Studio.\n"
                "❸ В установщике отметьте: 'C++ build tools'\n"
                "❹ В разделе 'Optional' включите 'MSVC v14.x', например 'MSVC v14.3x - VS 2022 C++ x64/x86 build tools'.\n"
                "❺ После установки закройте терминал, откройте новый CMD/PowerShell и запустите скрипт снова.\n"
                "====================\n"
            )
            url = "https://visualstudio.microsoft.com/visual-cpp-build-tools/"
            print(f"\nСайт откроется через 30 секунд...")
            for i in range(30, 0, -1):
                print(f"{i}...", end='', flush=True)
                time.sleep(1)
            print("\nОткрываю сайт: " + url)
            try:
                webbrowser.open(url)
            except Exception:
                print("Не удалось открыть браузер автоматически. Перейдите по ссылке вручную.")
        else:
            print("На этой ОС требуется установить компилятор C++ вручную согласно документации вашей платформы.")

        print("Ошибка установки:", e)
        sys.exit(1)

def environment_and_mode():
    setup_environment()
    MODE = "ALL"
    if not try_import_bip_utils():
        print("⚠️  Модуль 'bip_utils' не установлен. Solana-функции недоступны.\n")
        while True:
            print("1. Попробовать доустановить 'bip_utils' автоматически (нужен pip и компилятор C++)")
            print("2. Запустить только в режиме EVM-only (Solana будет отключён)")
            print("3. Выйти без запуска\n")
            user_choice = input("Ваш выбор [1/2/3]: ").strip()
            if user_choice == "1":
                install_bip_utils()
            elif user_choice == "2":
                MODE = "EVM-only"
                print("\nСкрипт работает в режиме: EVM-only\n")
                break
            elif user_choice == "3":
                print("\nВыход.")
                sys.exit(0)
            else:
                print("Некорректный выбор. Попробуйте ещё раз.\n")
    else:
        print("\nСкрипт работает в режиме: ALL (EVM + Solana)\n")
    return MODE

# --- БЛОК ОПЦИОНАЛЬНОГО ИМПОРТА ---

MODE = environment_and_mode()

from eth_account import Account
from mnemonic import Mnemonic
import base58
if MODE == "ALL":
    from bip_utils import Bip39SeedGenerator, Bip44, Bip44Coins, Bip44Changes

def all_lines(filepath: str):
    try:
        with open(filepath, 'r') as file:
            lines = file.readlines()
        return [line.strip() for line in lines if line.strip()] or False
    except FileNotFoundError:
        print(f"Файл {filepath} не найден.")
        return False

def add_line(filepath: str, line: str):
    with open(filepath, 'a') as file:
        file.write(line + '\n')

def clear_file(filepath: str):
    with open(filepath, 'w') as file:
        file.truncate(0)

def seed_to_evm_keypair(seed_phrase, account_index=0):
    try:
        Account.enable_unaudited_hdwallet_features()
        account = Account.from_mnemonic(
            seed_phrase.strip(),
            account_path=f"m/44'/60'/{account_index}'/0/0"
        )
        return {
            "address": account.address,
            "private_key": "0x" + account.key.hex(),
            "chain": "evm"
        }
    except Exception as e:
        print(f"Ошибка EVM: {str(e)}")
        return None

def seed_to_solana_keypair(seed_phrase, account_index=0):
    if MODE != "ALL":
        print("Solana не включена в данном режиме.")
        return None
    try:
        seed_bytes = Bip39SeedGenerator(seed_phrase.strip()).Generate()
        bip44_chg = Bip44.FromSeed(seed_bytes, Bip44Coins.SOLANA) \
            .Purpose() \
            .Coin() \
            .Account(account_index) \
            .Change(Bip44Changes.CHAIN_EXT)
        private_key = bip44_chg.PrivateKey().Raw().ToBytes()
        public_key = bip44_chg.PublicKey().RawCompressed().ToBytes()[1:]  # Убираем префикс

        private_key_full = private_key + public_key
        public_key_base58 = base58.b58encode(public_key).decode()
        private_key_base58 = base58.b58encode(private_key_full).decode()

        return {
            "address": public_key_base58,
            "private_key": private_key_base58,
            "chain": "solana"
        }
    except Exception as e:
        print(f"Ошибка Solana: {str(e)}")
        return None

def main_menu():
    print("[1] Mnemonic -> Private Key (EVM)")
    print("[2] Private Key -> Address (EVM)")
    print("[3] Mnemonic -> Address (EVM)")
    if MODE == "ALL":
        print("[4] Mnemonic -> Private Key (Solana)")
        print("[5] Mnemonic -> Address (Solana)")
    else:
        print("⏹ Solana-функции отключены — доступны только пункты EVM.\n")

    try:
        action = int(input("\n> "))
    except ValueError:
        print("Ошибка: Введите число.")
        return

    mnemonics = all_lines(filepath="mnemonics.txt")
    if not mnemonics and action in [1,3,4,5]:
        print("Файл mnemonics.txt пуст или не существует.")
        return

    if action == 1:
        clear_file(filepath="private_keys_evm.txt")
        for mnemonic in mnemonics:
            wallet = seed_to_evm_keypair(mnemonic)
            if wallet:
                add_line(filepath="private_keys_evm.txt", line=wallet["private_key"])
        print("Готово. Сохранено в private_keys_evm.txt")
    elif action == 3:
        clear_file(filepath="addresses_evm.txt")
        for mnemonic in mnemonics:
            wallet = seed_to_evm_keypair(mnemonic)
            if wallet:
                add_line(filepath="addresses_evm.txt", line=wallet["address"])
        print("Готово. Сохранено в addresses_evm.txt")
    elif action == 4 and MODE == "ALL":
        clear_file(filepath="private_keys_solana.txt")
        for mnemonic in mnemonics:
            wallet = seed_to_solana_keypair(mnemonic)
            if wallet:
                add_line(filepath="private_keys_solana.txt", line=wallet["private_key"])
        print("Готово. Сохранено в private_keys_solana.txt")
    elif action == 5 and MODE == "ALL":
        clear_file(filepath="addresses_solana.txt")
        for mnemonic in mnemonics:
            wallet = seed_to_solana_keypair(mnemonic)
            if wallet:
                add_line(filepath="addresses_solana.txt", line=wallet["address"])
        print("Готово. Сохранено в addresses_solana.txt")
    elif action == 2:
        private_keys = all_lines(filepath="private_keys_evm.txt")
        if private_keys:
            clear_file(filepath="addresses_evm.txt")
            for private_key in private_keys:
                try:
                    account = Account.from_key(private_key.strip())
                    add_line(filepath="addresses_evm.txt", line=account.address)
                except Exception as e:
                    print(f"Ошибка для ключа: {str(e)}")
            print("Готово. Сохранено в addresses_evm.txt")
        else:
            print("Файл private_keys_evm.txt пуст или не существует.")
    else:
        print("Ошибка: Неверный выбор действия или функция недоступна.")

if __name__ == "__main__":
    main_menu()
