
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

## HTTP API

API можно поднять локально и открыть наружу через ngrok. Через один публичный URL будут доступны и расчет, и временные ссылки на картинки.

### Переменные окружения

```env
API_HOST=127.0.0.1
API_PORT=8090
API_TOKEN=your-secret-token
PUBLIC_BASE_URL=https://your-ngrok-url.ngrok.app
IMAGE_API_BASE_URL=http://127.0.0.1:8090
API_RATE_LIMIT_REQUESTS=60
API_RATE_LIMIT_SECONDS=60
```

`PUBLIC_BASE_URL` должен указывать на тот же ngrok tunnel, который смотрит на `API_PORT`.
`IMAGE_API_BASE_URL` нужен старому Telegram-боту: он будет отправлять PNG в API, а API вернет публичную ссылку `PUBLIC_BASE_URL/images/...`.

### Запуск API

```bash
python -m app.run_api
ngrok http 8090
```

Если старый Telegram-бот тоже запущен, стартуйте API до бота. Тогда бот будет хранить картинки через API и отдельный `APP_PORT` для картинок ему не понадобится.

### Healthcheck

```bash
curl https://your-ngrok-url.ngrok.app/health
```

### Конвертация через текст команды

```bash
curl -X POST https://your-ngrok-url.ngrok.app/api/v1/convert \
  -H "Authorization: Bearer your-secret-token" \
  -H "Content-Type: application/json" \
  -d '{"text":"EUR USD 1000-0.3%","include_image":true}'
```

Для markup-режима через текст используйте двойной процент:

```bash
curl -X POST https://your-ngrok-url.ngrok.app/api/v1/convert \
  -H "Authorization: Bearer your-secret-token" \
  -H "Content-Type: application/json" \
  -d '{"text":"EUR USD 1000-0.3%%","include_image":true}'
```

### Конвертация через структурированный JSON

```bash
curl -X POST https://your-ngrok-url.ngrok.app/api/v1/convert \
  -H "Authorization: Bearer your-secret-token" \
  -H "Content-Type: application/json" \
  -d '{
    "from_currency": "EUR",
    "to_currency": "USD",
    "amount": "1000",
    "percent": "0.3",
    "sign": -1,
    "percent_mode": "%",
    "include_image": true
  }'
```

`percent_mode` поддерживает два режима:

- `"%"` — обычный процент: `converted * (1 +/- percent)`.
- `"%%"` — markup-расчет: `converted / (1 +/- percent)`.

Пример ответа:

```json
{
  "from_currency": "EUR",
  "to_currency": "USD",
  "amount": "1000",
  "rate": "1.1529",
  "converted": "1152.90",
  "percent": "0.3",
  "percent_mode": "%",
  "final_amount": "1149.441",
  "sign": -1,
  "is_markup": false,
  "image_url": "https://your-ngrok-url.ngrok.app/images/abc123.png"
}
```

### Загрузка картинки в API

Этот endpoint использует старый Telegram-бот, когда задан `IMAGE_API_BASE_URL`.

```bash
curl -X POST https://your-ngrok-url.ngrok.app/api/v1/images \
  -H "Authorization: Bearer your-secret-token" \
  -H "Content-Type: image/png" \
  --data-binary @card.png
```

Ответ:

```json
{
  "image_url": "https://your-ngrok-url.ngrok.app/images/abc123.png"
}
```

Rate limit применяется к `POST /api/v1/convert` и `POST /api/v1/images`.

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
