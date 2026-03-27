
# ConverterBot

Telegram-бот для конвертации валют с использованием данных с [XE.com](https://www.xe.com)  
Поддерживает комиссии и наценки.

---

## Возможности

- Актуальные курсы с XE (через внутренний API)
- Конвертация валют:
- Поддержка комиссий:
- Красивые карточки с результатом (PIL)
- Встроенный HTTP-сервер для изображений
- Безопасные временные ссылки на картинки

---

## 📌 Примеры использования

### Обычная конвертация

/xe AED 1000

1000 AED = 272.29 USD

---

### С комиссией

/xe EUR 100-0.3%



115.29 * 0.997 = 114.94

---

### С наценкой (markup)

/xe EUR 100-0.3%%



100 * 1.1529 / 1.003 = 114.94

---

### Inline режим

@ConverterBot EUR USD 1000-0.2%

## ⚙️ Установка
```bash
1. Клонировать проект

git clone https://github.com/your-username/converter-bot.git
cd converter-bot

2. Создать виртуальное окружение

python3 -m venv .venv
source .venv/bin/activate

3. Установить зависимости

pip install -r requirements.txt


⸻

🔐 Настройки (.env)

Создай файл .env:

BOT_TOKEN=your_telegram_token

XE_USERNAME=random_username
XE_PASSWORD=random_passwd
XE_BASE_URL=https://www.xe.com/api/protected/live-currency-pairs-rates/

APP_HOST=127.0.0.1
APP_PORT=8080

PUBLIC_BASE_URL=https://your-ngrok-url.ngrok.app

IMAGE_TTL_SECONDS=1800
IMAGE_MAX_ITEMS=500


⸻

▶️ Запуск

python -m app.run

⸻
```

🖼 Генерация изображений

    •	генерирация картинки через PIL
    •	хранение в memory store
    •	отдаем по временной ссылке
	•	автоматически удаляем по TTL

⸻

🔒 Безопасность
	
    •	порт 8080 не открывается наружу
⸻

🛠 Технологии

    •	Python 3.12+
	•	aiogram 3
	•	requests
	•	aiohttp
	•	Pillow (PIL)
	•	ngrok
