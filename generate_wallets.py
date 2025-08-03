# Файл: generate_wallets.py
import os
import sys
from pathlib import Path
import importlib.util
from datetime import datetime
import time
import json
import requests
from web3 import Web3

# Проверяем и устанавливаем необходимые пакеты
try:
    import openpyxl
except ImportError:
    print("Устанавливаю пакет 'openpyxl'...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "openpyxl"])
    import openpyxl

try:
    import requests
except ImportError:
    print("Устанавливаю пакет 'requests'...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
    import requests

try:
    from web3 import Web3
except ImportError:
    print("Устанавливаю пакет 'web3'...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "web3"])
    from web3 import Web3

# Проверяем, есть ли доступ к основному скрипту
main_script = Path("main.py")
if not main_script.exists():
    print("Ошибка: Основной скрипт main.py не найден.")
    sys.exit(1)

# Импортируем необходимые функции из основного скрипта
spec = importlib.util.spec_from_file_location("main", "main.py")
main = importlib.util.module_from_spec(spec)
spec.loader.exec_module(main)

# Получаем доступ к необходимым переменным и функциям
MODE = main.MODE
Account = main.Account
Mnemonic = main.Mnemonic
base58 = main.base58
seed_to_evm_keypair = main.seed_to_evm_keypair
seed_to_solana_keypair = main.seed_to_solana_keypair

# Публичные RPC для различных блокчейнов
PUBLIC_RPC_URLS = {
    "ethereum": [
        "https://eth.llamarpc.com",
        "https://ethereum.publicnode.com",
        "https://rpc.ankr.com/eth",
        "https://ethereum.blockpi.network/v1/rpc/public"
    ],
    "solana": [
        "https://api.mainnet-beta.solana.com",
        "https://solana-api.projectserum.com",
        "https://rpc.ankr.com/solana"
    ]
}

def get_evm_balance(address, chain="ethereum"):
    """Получает баланс для EVM-адреса через публичный RPC."""
    try:
        # Пробуем разные RPC пока не получим результат
        rpc_urls = PUBLIC_RPC_URLS.get(chain, PUBLIC_RPC_URLS["ethereum"])
        
        for rpc_url in rpc_urls:
            try:
                web3 = Web3(Web3.HTTPProvider(rpc_url))
                if web3.is_connected():
                    # Проверяем правильность формата адреса
                    if not web3.is_address(address):
                        print(f"Неверный формат адреса: {address}")
                        return "Неверный адрес"
                    
                    # Получаем баланс в wei
                    balance_wei = web3.eth.get_balance(Web3.to_checksum_address(address))
                    # Конвертируем в ETH
                    balance_eth = web3.from_wei(balance_wei, 'ether')
                    return f"{balance_eth:.6f} ETH"
                
            except Exception as e:
                print(f"RPC {rpc_url} недоступен: {e}")
                continue
        
        # Если ни один RPC не сработал
        return "Ошибка RPC"
    
    except Exception as e:
        print(f"Ошибка при получении баланса для {address}: {e}")
        return "Ошибка"

def get_solana_balance(address):
    """Получает баланс для Solana-адреса через публичный RPC."""
    try:
        # Пробуем разные RPC пока не получим результат
        for rpc_url in PUBLIC_RPC_URLS["solana"]:
            try:
                # Создаем JSON-RPC запрос
                payload = {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "getBalance",
                    "params": [address]
                }
                
                response = requests.post(rpc_url, json=payload)
                
                if response.status_code == 200:
                    data = response.json()
                    if "result" in data and "value" in data["result"]:
                        # Конвертируем из lamports в SOL (1 SOL = 10^9 lamports)
                        balance_sol = float(data["result"]["value"]) / 10**9
                        return f"{balance_sol:.6f} SOL"
                
            except Exception as e:
                print(f"RPC {rpc_url} недоступен: {e}")
                continue
        
        # Если ни один RPC не сработал
        return "Ошибка RPC"
    
    except Exception as e:
        print(f"Ошибка при получении баланса для {address}: {e}")
        return "Ошибка"

def save_wallets_to_excel(wallets, filename, chain="evm"):
    """Сохраняет информацию о кошельках в Excel файл, включая баланс."""
    if not wallets:
        print("Нет данных для сохранения в Excel.")
        return
    
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Wallets"
    
    # Добавляем заголовки
    ws.append(["Seed Phrase", "Address", "Private Key", "Balance"])
    
    # Настраиваем ширину столбцов
    ws.column_dimensions['A'].width = 60  # Для seed фразы
    ws.column_dimensions['B'].width = 45  # Для адреса
    ws.column_dimensions['C'].width = 70  # Для приватного ключа
    ws.column_dimensions['D'].width = 15  # Для баланса
    
    # Спрашиваем, нужно ли проверять балансы
    check_balances = input("Проверить балансы адресов? (да/нет): ").strip().lower() in ["да", "yes", "y", "д"]
    
    # Получаем балансы и добавляем данные
    total_wallets = len(wallets)
    for i, wallet in enumerate(wallets):
        if check_balances:
            print(f"Получение баланса для кошелька {i+1}/{total_wallets}...")
            
            if chain == "evm":
                balance = get_evm_balance(wallet["Address"])
            else:  # solana
                balance = get_solana_balance(wallet["Address"])
                
            # Добавляем случайную задержку между запросами для избежания блокировки RPC
            time.sleep(0.5 + (hash(wallet["Address"]) % 10) / 10)  # от 0.5 до 1.5 секунд
        else:
            balance = "N/A"
            
        ws.append([wallet["Seed Phrase"], wallet["Address"], wallet["PrivateKey"], balance])
    
    # Добавляем текущую дату и время к имени файла
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename_with_timestamp = f"{filename.split('.')[0]}_{timestamp}.xlsx"
    
    try:
        wb.save(filename_with_timestamp)
        print(f"✅ Данные успешно сохранены в файл '{filename_with_timestamp}'.")
    except Exception as e:
        print(f"❌ Ошибка при сохранении файла '{filename_with_timestamp}': {e}")

def generate_evm_wallets(count):
    """
    Генерирует count новых EVM кошельков.
    Для каждого кошелька: генерирует seed фразу, затем получает адрес и приватный ключ.
    """
    wallets = []
    for i in range(count):
        try:
            # Генерируем новую мнемонику
            seed_phrase = Mnemonic().generate()
            
            # Получаем адрес и приватный ключ из seed фразы
            keypair = seed_to_evm_keypair(seed_phrase)
            
            if keypair:
                # Добавляем данные в список кошельков для Excel
                wallets.append({
                    "Seed Phrase": seed_phrase,
                    "Address": keypair["address"],
                    "PrivateKey": keypair["private_key"]
                })
                print(f"✓ Сгенерирован EVM кошелек {i+1}/{count}")
            else:
                print(f"✗ Ошибка генерации EVM кошелька {i+1}/{count}")
                
        except Exception as e:
            print(f"✗ Ошибка при генерации EVM кошелька {i+1}/{count}: {e}")
    
    return wallets

def generate_solana_wallets(count):
    """
    Генерирует count новых Solana кошельков.
    Для каждого кошелька: генерирует seed фразу, затем получает адрес и приватный ключ.
    """
    if MODE != "ALL":
        print("Solana-функции недоступны, так как 'bip_utils' не установлен.")
        return []
    
    wallets = []
    for i in range(count):
        try:
            # Генерируем новую мнемонику
            seed_phrase = Mnemonic().generate()
            
            # Получаем адрес и приватный ключ из seed фразы
            keypair = seed_to_solana_keypair(seed_phrase)
            
            if keypair:
                # Добавляем данные в список кошельков для Excel
                wallets.append({
                    "Seed Phrase": seed_phrase,
                    "Address": keypair["address"],
                    "PrivateKey": keypair["private_key"]
                })
                print(f"✓ Сгенерирован Solana кошелек {i+1}/{count}")
            else:
                print(f"✗ Ошибка генерации Solana кошелька {i+1}/{count}")
                
        except Exception as e:
            print(f"✗ Ошибка при генерации Solana кошелька {i+1}/{count}: {e}")
    
    return wallets

def show_menu():
    """Отображает меню для генерации кошельков."""
    print("\n--- Генерация кошельков ---")
    print("1. Сгенерировать EVM кошельки и сохранить в Excel")
    if MODE == "ALL":
        print("2. Сгенерировать Solana кошельки и сохранить в Excel")
    print("0. Выход")
    
    choice = input("\nВыберите пункт: ")
    
    if choice == "1":
        try:
            count = int(input("Введите количество EVM кошельков для генерации: "))
            if count <= 0:
                print("Количество должно быть положительным числом.")
                return
        except ValueError:
            print("Некорректное число.")
            return
        
        wallets = generate_evm_wallets(count)
        if wallets:
            save_wallets_to_excel(wallets, "evm_wallets.xlsx", "evm")
    
    elif choice == "2" and MODE == "ALL":
        try:
            count = int(input("Введите количество Solana кошельков для генерации: "))
            if count <= 0:
                print("Количество должно быть положительным числом.")
                return
        except ValueError:
            print("Некорректное число.")
            return
        
        wallets = generate_solana_wallets(count)
        if wallets:
            save_wallets_to_excel(wallets, "solana_wallets.xlsx", "solana")
    
    elif choice == "0":
        print("Выход.")
        sys.exit(0)
    
    else:
        print("Неверный выбор. Попробуйте снова.")

if __name__ == "__main__":
    print("Скрипт для генерации кошельков и сохранения в Excel")
    show_menu()
