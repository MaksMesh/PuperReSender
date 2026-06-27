from telethon import TelegramClient
from telethon import events
from telethon.tl.types import DocumentAttributeFilename, MessageMediaPhoto, MessageMediaPoll, InputGeoPoint, InputMediaGeoPoint, MessageMediaGeo, UpdateMessageID
from telethon.tl.functions.channels import ToggleForumRequest
from telethon.tl.functions.messages import CreateForumTopicRequest, GetForumTopicsRequest, GetForumTopicsByIDRequest
from telethon.errors.rpcerrorlist import ApiIdInvalidError, PhoneNumberInvalidError, PasswordHashInvalidError
import asyncio
import argparse
import logging
import os
import settings
import tools
import json


logging.getLogger('telethon').setLevel(logging.WARNING)
config_file = 'config.json'


async def send_message(event, spy_chats, to_chat, client, text, media, topic_id, from_chat_id):
    if spy_chats[from_chat_id]['forum'] and bring_topics_from_source:
        name_topic = await client(GetForumTopicsByIDRequest(from_chat_id, [topic_id]))
        name_topic = name_topic.topics[0].title

        forums = await client(GetForumTopicsRequest(to_chat, 0, 0, 0, 100))
        forums_names = [j.title for j in forums.topics]
        forums_ids = [j.id for j in forums.topics]

        if name_topic in forums_names:
            reply_to = forums_ids[forums_names.index(name_topic)]
        else:
            topic = await client(CreateForumTopicRequest(to_chat, name_topic))
            
            for j in topic.updates:
                if type(j) is UpdateMessageID:
                    reply_to = j.id
                    break
    elif to_chat.forum and bring_topics_from_source:
        chat = await client.get_entity(from_chat_id)
        name_topic = chat.title

        forums = await client(GetForumTopicsRequest(to_chat, 0, 0, 0, 100))
        forums_names = [j.title for j in forums.topics]
        forums_ids = [j.id for j in forums.topics]

        if name_topic in forums_names:
            reply_to = forums_ids[forums_names.index(name_topic)]
        else:
            topic = await client(CreateForumTopicRequest(to_chat, name_topic))
            
            for j in topic.updates:
                if type(j) is UpdateMessageID:
                    reply_to = j.id
                    break
    else:
        reply_to = None

    if media is not None:
        if type(media) is MessageMediaPoll:
            message = f'**Опрос**\nНазвание: {media.poll.question.text}\nОписание: {text}\n\nВарианты ответов:\n'
            options = [i.text.text for i in media.poll.answers]
            await client.send_message(to_chat, message + '\n'.join(options), reply_to=reply_to)
        elif type(media) is MessageMediaGeo:
            geo_point = InputGeoPoint(media.geo.lat, media.geo.long)
            media = InputMediaGeoPoint(geo_point)

            await client.send_file(to_chat, media, reply_to=reply_to)
        else:
            name = ''
            video_note = False

            if type(media) is MessageMediaPhoto:
                name = str(media.photo.id) + '.jpg'
            else:
                if media.voice:
                    name = str(media.document.id) + '.ogg'
                elif media.round:
                    name = str(media.document.id) + '.mp4'
                    video_note = True
                else:
                    for i in media.document.attributes:
                        if type(i) is DocumentAttributeFilename:
                            name = i.file_name

            if not name:
                name = 'untitled'

            temp_file = open(os.path.join(files_dir, name), 'wb')
            file_name = temp_file.name

            await client.download_media(media, temp_file)

            await client.send_file(to_chat, file_name, caption=text, video_note=video_note, reply_to=reply_to)

            os.remove(file_name)
    else:
        await client.send_message(to_chat, text, reply_to=reply_to)
   

async def main():
    client = TelegramClient('session', api_id, api_hash, lang_code="ru", system_lang_code="ru-RU")

    def get_code():
        return input('Введите код: ').strip()

    await client.start(phone, password, code_callback=get_code)

    print('Вход выполнен.' if await client.is_user_authorized() else 'Войти не удалось.')

    to_chat = await client.get_entity(fin_chat)

    spy_chats = {}

    for i in source_chats:
        if '#' in i:
            chat_id, topic_ids = i.split('#')
            chat_id = int(chat_id)
            topic_ids = tuple(map(int, topic_ids.split(',')))
        else:
            chat_id = int(i)
            topic_ids = False

        chat_id = int(str(chat_id)[4:] if str(chat_id).startswith('-100') else str(abs(chat_id)))

        chat = await client.get_entity(chat_id)
        
        try:
            if chat.forum and topic_ids:
                spy_chats[chat_id] = {'spy_topics': topic_ids, 'forum': True}
            elif chat.forum:
                spy_chats[chat_id] = {'forum': True}
            else:
                spy_chats[chat_id] = {'forum': False}
        except Exception:
            spy_chats[chat_id] = {'forum': False}

        try:
            if to_chat.forum and bring_topics_from_source and not chat.forum:
                forums = await client(GetForumTopicsRequest(to_chat, 0, 0, 0, 100))
                forums = [j.title for j in forums.topics]
                
                if chat.title not in forums:
                    await client(CreateForumTopicRequest(to_chat, chat.title))
        except Exception:
            pass

        try:
            if chat.forum and bring_topics_from_source:
                if hasattr(to_chat, 'forum'):
                    if not to_chat.forum:
                        await client(ToggleForumRequest(to_chat, True, False))
                else:
                    await client(ToggleForumRequest(to_chat, True, False))

                forums = await client(GetForumTopicsRequest(chat, 0, 0, 0, 100))
                forums = [j.title for j in forums.topics]

                to_forums = await client(GetForumTopicsRequest(to_chat, 0, 0, 0, 100))
                to_forums = [j.title for j in to_forums.topics]

                for forum in forums:
                    if forum not in to_forums:
                        await client(CreateForumTopicRequest(to_chat, forum))
                        to_forums.append(forum)
        except Exception as e:
            pass

    @client.on(events.NewMessage(spy_chats))
    async def get_new_message(event):
        media = event.media
        text = event.message.message

        try:
            from_chat_id = event.message.peer_id.channel_id
        except Exception:
            from_chat_id = event.message.peer_id.chat_id

        topic_id = None

        if event.message.reply_to is not None:
            if getattr(event.message.reply_to, 'reply_to_top_id', False):
                topic_id = event.message.reply_to.reply_to_top_id
            elif getattr(event.message.reply_to, 'reply_to_msg_id', False):
                topic_id = event.message.reply_to.reply_to_msg_id

        if topic_id is None:
            topic_id = 1

        if mark_msg_source:
            chat = await client.get_entity(from_chat_id)
            chat_name = chat.title

            text = f'🧷 Переслано из группы "{chat_name}".\n' + text

        reqs = spy_chats[from_chat_id].get('spy_topics', [])

        if not reqs or topic_id in reqs:
            await send_message(event, spy_chats, to_chat, client, text, media, topic_id, from_chat_id)

    print('Ожидание сообщений...')

    await client.run_until_disconnected()


if __name__ == '__main__':
    parser = argparse.ArgumentParser('script', description='Скрипт для трансляции сообщений из одной группы в другую.')

    parser.add_argument('-s', '--settings', action='store_true', help='Включает режим настройки.')
    parser.add_argument('-t', '--tool', help='Вызывает инструмент с указанным названием. С неизвестным параметром выводит список инструментов.')

    args = parser.parse_args()

    if args.settings:
        settings.main()
    elif args.tool is not None:
        if args.tool == 'get_chat_id':
            tools.get_chat_id()
        else:
            print('Использование неизвестного инструмента. Доступные инструменты: "get_chat_id".')
    else:
        files_dir = os.path.join(os.path.curdir, 'files')

        if not os.path.exists(files_dir):
            os.mkdir(files_dir)

        if os.path.exists(config_file):
            try:
                with open(config_file) as file:
                    config = json.load(file)
            except Exception:
                print('Не удалось прочитать конфигурационный файл. Пересоздайте его используя флаг -s при запуске программы.')
            else:
                api_id = config.get('api_id', None)
                api_hash = config.get('api_hash', None)

                phone = config.get('phone', None)
                password = config.get('two_step_pass', '') # Двухфакторка

                source_chats = config.get('source_chats', None)
                fin_chat = config.get('fin_chat', None)

                bring_topics_from_source = config.get('bring_topics_from_source', True)
                mark_msg_source = config.get('mark_msg_source', False)

                if api_id is None:
                    print('Не указан параметр api_id.')
                elif api_hash is None:
                    print('Не указан параметр api_hash.')
                elif phone is None:
                    print('Не указан параметр phone.')
                elif source_chats is None:
                    print('Не указан параметр source_chats.')
                elif fin_chat is None:
                    print('Не указан параметр fin_chat.')
                else:
                    try:
                        asyncio.run(main())
                    except KeyboardInterrupt:
                        print('Остановка программы...')
                    except ApiIdInvalidError:
                        print('Неверно указан "api_id" или "api_hash".')
                    except PhoneNumberInvalidError:
                        print('Неверно указан номер телефона.')
                    except PasswordHashInvalidError:
                        print('Неверно пароль.')
        else:
            print('Не найден кофигурационный файл. Создайте его используя флаг -s при запуске программы.')