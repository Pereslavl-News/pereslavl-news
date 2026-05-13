# Типичный Переславль + Telegram-бот дилемм

## Где указать токен бота

Токен не нужно вставлять прямо в `bot.py`: он читается из переменной `TELEGRAM_BOT_TOKEN`.

Самый удобный способ для локального запуска — создать файл `.env` в корне проекта рядом с `bot.py`:

```env
TELEGRAM_BOT_TOKEN=твой_токен_от_BotFather
VOTES_DB=votes.db
```

В репозитории есть пример `.env.example`. Его можно скопировать:

```bash
cp .env.example .env
```

После этого открой `.env` и замени `123456789:replace_with_token_from_BotFather` на настоящий токен от [@BotFather](https://t.me/BotFather).

Файл `.env` уже добавлен в `.gitignore`, поэтому настоящий токен не попадёт в git.

## Установка и запуск бота

```bash
pip install -r requirements.txt
python bot.py
```

Если не хочешь использовать `.env`, токен можно передать прямо через переменную окружения:

```bash
TELEGRAM_BOT_TOKEN=твой_токен_от_BotFather python bot.py
```

В PowerShell:

```powershell
$env:TELEGRAM_BOT_TOKEN="твой_токен_от_BotFather"
python bot.py
```
