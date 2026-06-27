import json
import os


HELP_INFO = r'''Доступные команды:

"q", "quit" или "exit" - Выход и сохранение текущих настроек.
"no_save" - Выход без сохранения изменений.
"help" - Помощь.)
"show" - Отображение текущих настроек.
"set {Параметр} {Значение}" Устанавливает значение для параметра.
"on {Параметр}" - Задаёт значение True, параметру с булевым значением.
"off {Параметр}" - Задаёт значение False, параметру с булевым значением.

Дополнительные сведения по параметрам:

Обязательные параметры: "api_id", "api_hash", "phone", "source_chats", "fin_chat".
Параметры с булевым значением: "bring_topics_from_source", "mark_msg_source".
Параметры-списки: "source_chats".

Для указания значения параметров-списков, используйте ", " между их элементами. Примеры значений:
"abc" - Список из одного элемента.
"adga, 46, fad31" - Список из 3 элементов.

В элеметах параметра "source_chats" следует указывать id группы.

Параметр "source_chats" дополнительно поддерживает пересылку из определённых тем группы (если группа разделена на темы). Для этого в элементе списка, после указания id чата, следует приписать: \#1,2,5. Эта запись будет значить, что пересылка будет происходить из тем, с id 1, 2 и 5. Примеры:
"102475\#4,5" - Пересылка из группы с id "102475", из тем с id "4" и "5".
"47561\#1,2, 478" - Пересылка из группы с id "47561", из тем с id "1" и "2"; и пересылка всех сообщений из группы с id "478".'''


def main():
    config_file = 'config.json'

    if os.path.exists(config_file):
        try:
            with open(config_file) as file:
                config = json.load(file)
        except Exception:
            config = {}
    else:
        config = {}

    print('Запущен режим настройки. Введите "help" для помощи.')

    while True:
        text = input('> ').strip()
        no_save = False

        if text == 'q' or text == 'quit' or text == 'exit':
            break
        elif text == 'no_save':
            no_save = True
            break
        elif text == 'help':
            print(HELP_INFO)
        elif text == 'show':
            print('api_id:', config.get('api_id', None))
            print('api_hash:', config.get('api_hash', None))
            print('phone:', config.get('phone', None))
            print('two_step_pass:', config.get('two_step_pass', None))
            print('source_chats:', config.get('source_chats', None))
            print('fin_chat:', config.get('fin_chat', None))
            print('bring_topics_from_source:', config.get('bring_topics_from_source', True))
            print('mark_msg_source:', config.get('mark_msg_source', False))
        elif text:
            text = text.split()

            if len(text) < 2:
                print('Неверная команда.')
            else:
                if text[0] == 'set':
                    if len(text[1:]) == 2:
                        param, value = text[1:]

                        if param in ['api_hash', 'phone', 'two_step_pass', 'fin_chat']:
                            config[param] = value
                        elif param == 'api_id':
                            try:
                                config[param] = int(value)
                            except Exception:
                                print('Значение api_id должно быть числом.')
                        elif param == 'source_chats':
                            config[param] = value.split(', ')
                        else:
                            print('Изменение неизвестного параметра.')
                    else:
                        if text[1] == 'source_chats':
                            config[text[1]] = ' '.join(text[2:]).split(', ')
                        else:
                            print('Неверный формат команды.')
                elif text[0] == 'on':
                    if len(text) == 2:
                        param = text[1]

                        if param in ['bring_topics_from_source', 'mark_msg_source']:
                            config[param] = True
                        else:
                            print('Изменение неизвестного параметра.')
                    else:
                        print('Неверный формат команды.')
                elif text[0] == 'off':
                    if len(text) == 2:
                        param = text[1]

                        if param in ['bring_topics_from_source', 'mark_msg_source']:
                            config[param] = False
                        else:
                            print('Изменение неизвестного параметра.')
                    else:
                        print('Неверный формат команды.')
                else:
                    print('Неверная команда.')
        else:
            print('Неверная команда.')

    if not no_save:
        with open(config_file, 'w') as file:
            json.dump(config, file, ensure_ascii=False, indent=4)