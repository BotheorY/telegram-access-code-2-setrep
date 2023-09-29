from utilities import wait_key, add_item_to_menus, remove_item_from_menus
from consolemenu import *
from consolemenu.items import *
from setrepcli import SetRepClient
from consolemenu import prompt_utils as pu
from constants import *
from telethon.sync import TelegramClient
from telethon.sessions import StringSession
import sys
import os
import json
from datetime import datetime

prompt: pu.PromptUtils = pu.PromptUtils(Screen())
menus: list[ConsoleMenu] = []

user_key: str = ''
user_token: str = ''
set_rep: SetRepClient = None
settings: list = None
telegram_session: str = ''
target_keys: list = []

config_mode: bool = False

def proc_target_keys(access_code: str):
    value: str = json.dumps({'datetime': datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'code': access_code})
    for target_key in target_keys:
        setrep = SetRepClient(SETREP_BASE_URL, user_key, user_token, target_key['app'])
        setrep.set_key_value(target_key['section'], target_key['key'], value)

def get_string_session()->str:
    global config_mode, user_key, user_token
    try:
        if len(sys.argv) > 1:
            for par in sys.argv[1:]:
                par = par.strip()
                if par == '-s':
                    config_mode = True
                if len(par) > 2:
                    if (not user_key) and (par[:2] == '-k'):
                        user_key = par[2:]
                    if (not user_token) and (par[:2] == '-t'):
                        user_token = par[2:]
        if not user_key:
            user_key = prompt.input(prompt = "Insert user key:", enable_quit = True)[0]
        if not user_token:
            user_token = prompt.input(prompt = "Insert user token:", enable_quit = True)[0]
        get_settings(user_key, user_token)
        if set_rep and (not telegram_session):
            set_telegram_session()
    except Exception as e:
        if str(e):
            print(f"[ERROR] {str(e)}")
    finally:
        return telegram_session
    
def set_telegram_session():
    global telegram_session
    print("Getting Telegram session string...")
    telegram_session = ''
    with TelegramClient(StringSession(), os.environ.get('BT_TELEGRAM_API_ID').strip(), os.environ.get('BT_TELEGRAM_API_HASH').strip()) as client:
        telegram_session = client.session.save()
    if telegram_session:
        set_rep.set_key_value('main', 'session', telegram_session)
    return telegram_session

def mnu_add_to_list(menu: ConsoleMenu) -> None:
    if menu:
        menus.append(menu)

def get_settings(user_key: str, user_token: str) -> list:
    global set_rep, settings, telegram_session, target_keys
    print("Loading settings...")
    try:
        set_rep = SetRepClient(SETREP_BASE_URL, user_key, user_token, APP_CODE)
        settings = set_rep.get_section_keys_values('main')
        telegram_session = set_rep.get_key_value('main', 'session')
        tkeys = set_rep.get_key_value('main', 'targetkeys')
        if tkeys:
            target_keys = json.loads(tkeys)
    except Exception as e:
        set_rep = None
        if str(e):
            print(f"[ERROR] {str(e)}")
    finally:
        print("Loading settings finished.")

def add_target_key() -> None: 
    print("Adding target key...")
    yet_exists: bool = True
    while yet_exists:
        new_item_name = prompt.input(prompt = "Name:")[0]
        yet_exists = target_key_name_exists(new_item_name)
        if yet_exists:
            print("Duplicate name. Choose another name...")
    new_item_app = prompt.input(prompt = "App code:")[0]
    new_item_section = prompt.input(prompt = "Section code:")[0]
    new_item_key = prompt.input(prompt = "Key code:")[0]
    new_item = {
        "name": new_item_name,
        "app": new_item_app,
        "section": new_item_section,
        "key": new_item_key
    }    
    target_keys.append(new_item)
    try:
        save_target_keys()
    except Exception as e:
        target_keys.pop(len(target_keys) - 1)
        print(f"[ERROR] {str(e)}. Operation aborted.")
    else:
        del_item: FunctionItem = FunctionItem(new_item_name, del_target_key, [len(target_keys) - 1])
        view_item: FunctionItem = FunctionItem(new_item_name, view_target_key, [len(target_keys) - 1])
        add_item_to_menus(menus, del_item, ['Delete Target Key'], False)
        add_item_to_menus(menus, view_item, ['View Target Key'], False)
        print(f"{new_item_name} created.")
    wait_key()

def del_target_key(index: int) -> None:
    key_data = target_keys[index]
    key_name = key_data['name']
    target_keys.pop(index)
    try:
        save_target_keys()
    except Exception as e:
        target_keys.insert(index, key_data)
        print(f"[ERROR] {str(e)}. Operation aborted.")
    else:
        remove_item_from_menus(menus, key_name)
        print(key_name + " deleted.")
    wait_key()

def get_mnu_delete_target_keys() -> list[dict]:
    result = []
    for index, target_key in enumerate(target_keys):
        result.append({"title": target_key['name'], "type": "func", "exec": "core.del_target_key", "args": [index]})
    return result

def view_target_key(index: int) -> None:
    print("Target key data...\n")
    key_data = target_keys[index]
    print(f"NAME        : {key_data['name']}\nAPP CODE    : {key_data['app']}\nSECTION CODE: {key_data['section']}\nKEY CODE    : {key_data['key']}\n")
    wait_key()

def get_mnu_view_target_keys() -> list[dict]:
    result = []
    for index, target_key in enumerate(target_keys):
        result.append({"title": target_key['name'], "type": "func", "exec": "core.view_target_key", "args": [index]})
    return result

def target_key_name_exists(name: str)->bool:
    found = False
    name = name.strip().upper()
    for item in target_keys:
        if item.get("name").strip().upper() == name:
            found = True
            break
    return found

def save_target_keys():
    value: str = json.dumps(target_keys)
    set_rep.set_key_value('main', 'targetkeys', value)
