import requests
from modelos.Credencial import get_credential_by_name


class TelegramHelper:
    def send_telegram_message(message):
        token = get_credential_by_name('TELEGRAM_TOKEN')
        chat_id = get_credential_by_name('TELEGRAM_CHAT_ID')
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        data = {
            "chat_id": chat_id,
            "text": message
        }
        try:
            response = requests.post(url, data=data)
            return response.json()
        except Exception as e:
            print(f"Error al enviar mensaje de Telegram: {e}")