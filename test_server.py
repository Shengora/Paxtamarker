from aiogram.client.telegram import TelegramAPIServer
server = TelegramAPIServer.from_base('https://paxta.online')
print(server.api_url(token="973:27RN6mvIdmW-qjzL-WiUOM9cGWDfVzQOrIH", method="getMe"))
