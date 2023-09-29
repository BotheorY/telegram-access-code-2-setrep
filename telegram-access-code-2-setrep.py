from menu import run_menu as rm, create_menu as cm
import core
from telethon.sync import TelegramClient
from telethon.sessions import StringSession
from telethon import events
from constants import *
import os

try:
    client = TelegramClient(StringSession(core.get_string_session()), os.environ.get('BT_TELEGRAM_API_ID').strip(), os.environ.get('BT_TELEGRAM_API_HASH').strip())
except Exception as e:
    ...

def process_message(msg: str)-> str:
    parts: list = msg.split('**')
    if len(parts) > 2:
        parts = parts[2].split('.')
        if len(parts) > 0:
            msg = parts[0].strip()
    if msg.isdigit():
        return msg
    else:
        return ''

async def do_run():
    await client.start()

    @client.on(events.NewMessage(incoming=True))
    async def handler(event):
        if event.is_private:
            from_user = await event.get_sender()
            user_name = from_user.first_name
            if user_name == 'Telegram':
                message_text = event.text
                access_code: str = process_message(message_text)
                try:
                    core.set_rep.set_key_value('main', 'lastmsg', f'Messaggio da {user_name}: {message_text}')
                    if access_code:
                        core.proc_target_keys(access_code)
                        print('Message saved!')
                    else:
                        print('Message not saved cause no code found.')
                except Exception as e:
                    print(f"Error saving message: {e}")

    await client.run_until_disconnected()

def main() -> None:

    try:

        menu: dict =    {
                            "title": "MAIN MENU",
                            "items":    [
                                            {"title": "Add Target Key", "type": "func", "exec": "core.add_target_key"},
                                            {"title": "View Target Keys...",
                                                "submenu":  {
                                                                "title": "View Target Key",
                                                                "subtitle": "Choose the Target Key to view:",
                                                                "items": "core.get_mnu_view_target_keys"
                                                            }
                                            },
                                            {"title": "Delete Target Key...",
                                                "submenu":  {
                                                                "title": "Delete Target Key",
                                                                "subtitle": "Choose the Target Key to delete:",
                                                                "items": "core.get_mnu_delete_target_keys"
                                                            }
                                            }
                                        ]
                        }
        err: list = [False, None, None]
        err_msg: str = None
        res = rm(cm(menu, err))

        if err[0]:
            err_msg = err[1]

        if res:
            if err_msg:
                err_msg = err_msg + " \n" + res
            else:
                err_msg = res

        if err_msg:
            raise Exception(err_msg)

    except Exception as e:
        if str(e):
            print(f"[ERROR] {str(e)}")


if __name__ == '__main__':
    if (core.config_mode):
        main()
    else:
        if core.set_rep and core.telegram_session:
            print('Running...')   
            import asyncio
            try:
                asyncio.get_event_loop().run_until_complete(do_run())
            except Exception as e:
                ...
