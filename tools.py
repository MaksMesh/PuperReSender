from telethon import TelegramClient
import asyncio
import json
import os


config_file = 'config.json'
HELP_INFO = r'''Доступные команды:

"q", "quit" или "exit" - Выход и сохранение текущих настроек.
"help" - Помощь.)
"list {n}" - Выводит список всех чатов и их id, если "n" не указан, иначе выводит первые n чатов и их id (порядок как в приложении Telegram).
"search {text}" - Ищет чаты, которые содержат подстроку "text" в названии, и выводит и названия и id.'''


def get_chat_id():
    async def main():
        client = TelegramClient('session', api_id, api_hash, lang_code="ru", system_lang_code="ru-RU")

        def get_code():
            return input('Введите код: ').strip()

        await client.start(phone, password, code_callback=get_code)

        print('Вход выполнен.' if await client.is_user_authorized() else 'Войти не удалось.')

        print('Введите "help" для помощи.')

        while True:
            command = input('> ').strip()

            if command:
                if command == 'list':
                    async for i in client.iter_dialogs():
                        print(i.name, i.id)
                elif command in ['q', 'quit', 'exit']:
                    break
                elif command == 'help':
                    print(HELP_INFO)
                else:
                    command = command.split()

                    if len(command) == 2:
                        com, val = command

                        if com == 'list':
                            try:
                                val = int(val)

                                async for i in client.iter_dialogs(val):
                                    print(i.name, i.id)
                            except Exception:
                                print('Неверный параметр.')
                        elif com == 'search':
                            val = val.strip().lower()
                            async for i in client.iter_dialogs():
                                if val in i.name.strip().lower():
                                    print(i.name, i.id)
                        else:
                            print('Неизвестная команда.')
                    else:
                        print('Неверная команда.')
            else:
                print('Неверная команда.')

        print('Завершение выполнения...')


    print('Запуск инструмента "get_chat_id"...')
    
    if os.path.exists(config_file):
        try:
            with open(config_file) as file:
                config = json.load(file)
        except Exception:
            print('Не удалось прочитать конфигурационный файл. Пересоздайте его используя флаг -s при запуске программы. Для работы данного инструмента необхожимы параметры "api_id", "api_hash" и "phone".')
        else:
            api_id = config.get('api_id', None)
            api_hash = config.get('api_hash', None)

            phone = config.get('phone', None)
            password = config.get('two_step_pass', '') # Двухфакторка

            if api_id is None:
                print('Не указан параметр api_id.')
            elif api_hash is None:
                print('Не указан параметр api_hash.')
            elif phone is None:
                print('Не указан параметр phone.')
            else:
                asyncio.run(main())
    else:
        print('Не найден кофигурационный файл. Создайте его используя флаг -s при запуске программы.')