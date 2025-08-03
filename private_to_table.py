# private_to_table.py
import os
import sys
from pathlib import Path
import openpyxl
from web3 import Web3
import base58
import requests
from datetime import datetime
import time

# Расширенные публичные RPC для различных EVM-сетей
PUBLIC_RPC_URLS = {
    "ethereum": [
        "https://eth.llamarpc.com",
        "https://ethereum.publicnode.com",
        "https://rpc.ankr.com/eth"
    ],
    "bsc": [
        "https://bsc-dataseed.binance.org",
        "https://bsc-dataseed1.defibit.io",
        "https://rpc.ankr.com/bsc"
    ],
    "polygon": [
        "https://polygon-rpc.com",
        "https://rpc-mainnet.matic.quiknode.pro",
        "https://rpc.ankr.com/polygon"
    ],
    "avalanche": [
        "https://api.avax.network/ext/bc/C/rpc",
        "https://rpc.ankr.com/avalanche"
    ],
    "arbitrum": [
        "https://arb1.arbitrum.io/rpc",
        "https://rpc.ankr.com/arbitrum"
    ],
    "optimism": [
        "https://mainnet.optimism.io",
        "https://rpc.ankr.com/optimism"
    ],
    "fantom": [
        "https://rpc.ftm.tools",
        "https://rpc.ankr.com/fantom"
    ],
    "solana": [
        "https://api.mainnet-beta.solana.com",
        "https://solana-api.projectserum.com"
    ]
}

# Нативные токены для каждой сети
NATIVE_TOKENS = {
    "ethereum": "ETH",
    "bsc": "BNB",
    "polygon": "MATIC",
    "avalanche": "AVAX",
    "arbitrum": "ETH",
    "optimism": "ETH",
    "fantom": "FTM",
    "solana": "SOL"
}

def get_evm_balance(address, chain="ethereum"):
    """Получает баланс для EVM-адреса в указанной сети"""
    try:
        rpc_urls = PUBLIC_RPC_URLS.get(chain, [])
        if not rpc_urls:
            return f"Unsupported chain: {chain}"
        
        for rpc_url in rpc_urls:
            try:
                web3 = Web3(Web3.HTTPProvider(rpc_url))
                if web3.is_connected():
                    if not web3.is_address(address):
                        return "Invalid address"
                    
                    balance_wei = web3.eth.get_balance(Web3.to_checksum_address(address))
                    balance = web3.from_wei(balance_wei, 'ether')
                    return f"{balance:.6f} {NATIVE_TOKENS.get(chain, 'ETH')}"
            except Exception as e:
                print(f"RPC error ({chain}): {e}")
                continue
        
        return "RPC error"
    except Exception as e:
        print(f"Balance check error ({chain}): {e}")
        return "Error"

def get_solana_balance(address):
    """Получает баланс для Solana-адреса"""
    try:
        for rpc_url in PUBLIC_RPC_URLS["solana"]:
            try:
                payload = {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "getBalance",
                    "params": [address]
                }
                response = requests.post(rpc_url, json=payload, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    if "result" in data and "value" in data["result"]:
                        balance_sol = float(data["result"]["value"]) / 10**9
                        return f"{balance_sol:.6f} SOL"
            except Exception as e:
                print(f"Solana RPC error: {e}")
                continue
        return "RPC error"
    except Exception as e:
        print(f"Solana balance error: {e}")
        return "Error"

def private_to_address_evm(private_key):
    """Конвертирует приватный ключ EVM в адрес"""
    try:
        account = Web3().eth.account.from_key(private_key.strip())
        return account.address
    except Exception as e:
        print(f"EVM key conversion error: {e}")
        return None

def private_to_address_solana(private_key):
    """Конвертирует приватный ключ Solana в адрес"""
    try:
        decoded = base58.b58decode(private_key)
        public_key_bytes = decoded[32:]
        return base58.b58encode(public_key_bytes).decode()
    except Exception as e:
        print(f"Solana key conversion error: {e}")
        return None

def process_private_keys(file_path, chain_type, networks=None):
    """Обрабатывает приватные ключи для указанных сетей"""
    results = []
    
    try:
        with open(file_path, 'r') as file:
            private_keys = [line.strip() for line in file if line.strip()]
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return []
    
    total_keys = len(private_keys)
    print(f"Processing {total_keys} private keys...")
    
    for i, private_key in enumerate(private_keys):
        row = {"Private Key": private_key}
        
        if chain_type == "evm":
            address = private_to_address_evm(private_key)
            if not address:
                continue
                
            row["Address"] = address
            
            if networks:
                for network in networks:
                    balance = get_evm_balance(address, network)
                    row[f"{network.upper()} Balance"] = balance
                    time.sleep(0.3)  # Rate limiting
        
        elif chain_type == "solana":
            address = private_to_address_solana(private_key)
            if not address:
                continue
                
            row["Address"] = address
            balance = get_solana_balance(address)
            row["SOL Balance"] = balance
            time.sleep(0.3)
        
        results.append(row)
        print(f"Processed {i+1}/{total_keys}")
    
    return results

def save_to_excel(data, filename_prefix, chain_type):
    """Сохраняет данные в Excel с динамическими колонками"""
    if not data:
        print("No data to save")
        return
    
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Wallets"
    
    # Определяем заголовки из первого элемента
    headers = list(data[0].keys())
    ws.append(headers)
    
    # Настраиваем ширину столбцов
    for col in ws.columns:
        column = col[0].column_letter
        if column == 'A':
            ws.column_dimensions[column].width = 70  # Private Key
        elif "Address" in col[0].value:
            ws.column_dimensions[column].width = 45  # Address
        else:
            ws.column_dimensions[column].width = 20  # Balances
    
    # Добавляем данные
    for row in data:
        ws.append([row.get(header, "") for header in headers])
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{filename_prefix}_{chain_type}_{timestamp}.xlsx"
    
    try:
        wb.save(filename)
        print(f"Saved to: {filename}")
    except Exception as e:
        print(f"Save error: {e}")

def select_evm_networks():
    """Выбор сетей для проверки баланса"""
    print("\nAvailable EVM networks:")
    networks = list(PUBLIC_RPC_URLS.keys())
    evm_networks = [n for n in networks if n != "solana"]
    
    for i, net in enumerate(evm_networks, 1):
        print(f"{i}. {net.upper()}")
    
    print("\nSelect networks to check (comma separated, or 'all'):")
    selection = input("> ").strip().lower()
    
    if selection == "all":
        return evm_networks
    else:
        selected = []
        for num in selection.split(','):
            try:
                idx = int(num.strip()) - 1
                if 0 <= idx < len(evm_networks):
                    selected.append(evm_networks[idx])
            except ValueError:
                continue
        return selected if selected else ["ethereum"]

def main():
    print("\n=== Private Keys to Addresses & Balances ===")
    print("\nSupported chains:")
    print("1. EVM (Multiple networks)")
    print("2. Solana")
    
    choice = input("\nSelect chain type (1/2): ").strip()
    
    if choice == "1":
        chain_type = "evm"
        input_file = "private_keys_evm.txt"
        output_prefix = "evm_wallets"
        networks = select_evm_networks()
    elif choice == "2":
        chain_type = "solana"
        input_file = "private_keys_solana.txt"
        output_prefix = "solana_wallets"
        networks = None
    else:
        print("Invalid choice")
        return
    
    if not os.path.exists(input_file):
        print(f"File {input_file} not found. Generate it first.")
        return
    
    check_balances = input("Check balances? (y/n): ").lower() == 'y'
    if not check_balances:
        networks = None
    
    data = process_private_keys(input_file, chain_type, networks)
    if data:
        save_to_excel(data, output_prefix, chain_type)
    else:
        print("No valid keys processed")

if __name__ == "__main__":
    try:
        import openpyxl
    except ImportError:
        print("Installing openpyxl...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "openpyxl"])
    
    main()
