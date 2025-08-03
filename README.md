
<p align="center">
  <picture>
    <img alt="Генератор Криптографических Ключей" src="figures/logo.png" width="50%">
  </picture>
</p>

<h1 align="center">Генератор Криптографических Ключей</h1>

[![Build Status](https://img.shields.io/badge/Сборка-Успешна-brightgreen)](https://github.com/KoTiRiKi/crypto-keypair-generator/actions) [![License](https://img.shields.io/badge/Лицензия-MIT-blue.svg)](LICENSE)

## ⚠️ Важное уведомление

Если вы используете этот скрипт для генерации ключей, убедитесь, что ваши мнемонические фразы соответствуют стандарту BIP-39. Недопустимые или неполные фразы могут привести к ошибкам или небезопасным ключам. Используйте в **офлайн-среде**. Никогда не делитесь приватными ключами.

➡️ [Упрощённая версия](https://github.com/KotikRiki/crypto-keypair-generator)

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
<div data-scrollable-x="true" class="overflow-auto scrollbar-transparent-track" style="width:calc(100% + 0.75rem * 2);margin-left:-0.75rem;margin-right:-0.75rem;padding-left:0.75rem;padding-right:0.75rem"><table class="w-full px-3"><thead><tr><th class="whitespace-nowrap">№</th><th class="whitespace-nowrap">Описание</th><th class="whitespace-nowrap">Вывод</th></tr></thead><tbody><tr><td>1</td><td>Mnemonic → Private Key (EVM)</td><td><code class="inline-code-block">private_keys_evm.txt</code></td></tr><tr><td>2</td><td>Private Key → Address (EVM)</td><td><code class="inline-code-block">addresses_evm.txt</code></td></tr><tr><td>3</td><td>Mnemonic → Address (EVM)</td><td><code class="inline-code-block">addresses_evm.txt</code></td></tr><tr><td>4</td><td>Mnemonic → Private Key (Solana)</td><td><code class="inline-code-block">private_keys_solana.txt</code></td></tr><tr><td>5</td><td>Mnemonic → Address (Solana)</td><td><code class="inline-code-block">addresses_solana.txt</code></td></tr><tr><td>6</td><td>Генерация кошельков и сохранение в Excel</td><td><code class="inline-code-block">wallets_{дата}.xlsx</code></td></tr><tr><td>7</td><td>Таблица: Приватники → Адреса и балансы (EVM)</td><td><code class="inline-code-block">addresses_with_balances.csv</code></td></tr></tbody></table></div>
<blockquote class="not-italic">

> ⚠️ Если модуль `bip_utils` не установлен, Solana-опции будут недоступны.

## 🔒 Безопасность

- Никогда не публикуйте `mnemonics.txt`, `private_keys_*.txt`
- Работайте в офлайн-среде
- Удаляйте чувствительные данные вручную после использования

## 🤝 Вклад

Pull request'ы и предложения приветствуются через [Issues](https://github.com/KoTiRiKi/crypto-keypair-generator/issues)!

## 📜 Лицензия

Проект распространяется под лицензией **MIT**. Подробнее в [LICENSE](LICENSE).
