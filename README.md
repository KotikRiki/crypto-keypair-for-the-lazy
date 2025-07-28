
<p align="center">
  <picture>
    <img alt="Генератор Криптографических Ключей" src="figures/logo.png" width="50%">
  </picture>
</p>

<h1 align="center">Генератор Криптографических Ключей</h1>

[![Build Status](https://img.shields.io/badge/Сборка-Успешна-brightgreen)](https://github.com/KoTiRiKi/crypto-keypair-generator/actions) [![License](https://img.shields.io/badge/Лицензия-MIT-blue.svg)](LICENSE)

## ⚠️ Важное уведомление

Если вы используете этот скрипт для генерации ключей, убедитесь, что ваши мнемонические фразы соответствуют стандарту BIP-39. Недопустимые или неполные фразы могут привести к ошибкам или небезопасным ключам. Используйте в **офлайн-среде**. Никогда не делитесь приватными ключами.

➡️ Упрощённая версия: https://github.com/KotikRiki/crypto-keypair-for-the-lazy

## 📰 Новости

- 📅 **[28.07.2025]** Первый релиз Crypto Keypair Generator на GitHub!

## 🔭 Обзор

Этот Python-скрипт позволяет **генерировать ключевые пары Ethereum (EVM) и Solana** из мнемонических фраз BIP-39. Скрипт автоматически создаёт виртуальное окружение и устанавливает зависимости.

## 🚀 Возможности

- ✅ Генерация приватных ключей и адресов EVM
- ✅ Генерация приватных ключей и адресов Solana
- ✅ Чтение мнемоник из `mnemonics.txt`
- ✅ Автоматическая установка зависимостей
- ✅ EVM-only режим при отсутствии компилятора C++

## 📦 Запуск и установка

Скрипт сам создаст `venv` и установит библиотеки. Просто скачайте и запустите:

```bash
git clone https://github.com/KoTiRiKi/crypto-keypair-generator.git
cd crypto-keypair-generator
python seed_to_private_evm_solana.py
```

Во время первого запуска:

- Будет создано виртуальное окружение
- Установятся нужные модули: `eth_account`, `mnemonic`, `base58`, `bip_utils`
- Если не установлен `bip_utils`, скрипт предложит:
  - Установить его (нужен C++ компилятор, Visual C++ для Windows)
  - Запустить только в режиме EVM

## 🎮 Использование

1. Создайте файл `mnemonics.txt` в директории проекта. Введите мнемоники по одной на строку:
```
example mnemonic phrase here ...
```

2. Запустите скрипт:
```bash
python seed_to_private_evm_solana.py
```

3. Выберите опцию:

| № | Описание | Вывод |
|--|----------|-------|
| 1 | Mnemonic → Private Key (EVM) | `private_keys_evm.txt` |
| 2 | Private Key → Address (EVM) | `addresses_evm.txt` |
| 3 | Mnemonic → Address (EVM) | `addresses_evm.txt` |
| 4 | Mnemonic → Private Key (Solana) | `private_keys_solana.txt` |
| 5 | Mnemonic → Address (Solana) | `addresses_solana.txt` |

> ⚠️ Если модуль `bip_utils` не установлен, Solana-опции будут недоступны.

## 🔒 Безопасность

- Никогда не публикуйте `mnemonics.txt`, `private_keys_*.txt`
- Работайте в офлайн-среде
- Удаляйте чувствительные данные вручную после использования

## 🤝 Вклад

Pull request'ы и предложения приветствуются через [Issues](https://github.com/KoTiRiKi/crypto-keypair-generator/issues)!

## 📜 Лицензия

Проект распространяется под лицензией **MIT**. Подробнее в [LICENSE](LICENSE).
