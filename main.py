from telethon import TelegramClient, events
import requests
from datetime import datetime, timezone

import db
from background import send_validator_updates_interval, send_vote_updates_interval, fetch_point_updates_interval, \
    check_block_validator_interval
from dotenv import load_dotenv
import os

load_dotenv()

bot_token = os.getenv('BOT_TOKEN')
api_id = os.getenv('API_ID')
api_hash = os.getenv('API_HASH')
client = TelegramClient("bot", api_id=api_id, api_hash=api_hash)
RPC = os.getenv('RPC') + "/status"
QUERY = ""
EMPTY = ""
CMD_VALIDATOR = "/validator"
CMD_MY_VALIDATOR = "/my_validator"
CMD_UPDATE_MY_VALIDATOR = "/update_my_validator"
CMD_NETWORK = "/network"
CMD_POINT = "/point"


def humanize_time_difference(delta):
    seconds = delta.total_seconds()

    if seconds < 60:
        return f"{round(seconds)} seconds ago"
    elif seconds < 3600:
        return f"{round(seconds // 60)} minutes ago"
    elif seconds < 86400:
        return f"{round(seconds // 3600)} hours ago"
    else:
        return f"{round(seconds // 86400)} days ago"


def get_network_status():
    try:
        r = requests.get(RPC)

        if r.status_code == 200:
            json_data = r.json()

            if 'result' in json_data:
                result = json_data['result']

                network_name = result.get('node_info', {}).get('network', 'N/A')
                block_height = result.get('sync_info', {}).get('latest_block_height', 'N/A')

                # Parse latest block time and calculate last update time
                latest_block_time_str = result.get('sync_info', {}).get('latest_block_time')
                if latest_block_time_str:
                    # Truncate to microseconds precision
                    latest_block_time_str = latest_block_time_str[:-1]
                    dot_index = latest_block_time_str.rfind('.')
                    latest_block_time_str = latest_block_time_str[:dot_index + 7]

                    latest_block_time = datetime.strptime(latest_block_time_str, "%Y-%m-%dT%H:%M:%S.%f").replace(
                        tzinfo=timezone.utc)
                    now = datetime.now(timezone.utc)
                    update_time_diff = now - latest_block_time
                    last_time_update = humanize_time_difference(update_time_diff)
                else:
                    last_time_update = 'N/A'

                # get epoch , use my rpc
                response = requests.get("http://65.21.29.119:6969/epoch")
                epoch = response.json()
                data_string = f"""```
Network Name       : {network_name}
Current epoch      : {epoch["epoch"]}
Block Height       : {block_height}
Last Time Update   : {last_time_update}
```"""

                return data_string

            else:
                return "Error to get network status"
        else:
            return "Error to get network status"
    except Exception as e:
        print(e)
        return "Error to get network status"


def get_latest_block():
    try:
        r = requests.get(RPC)
        if r.status_code == 200:
            json_data = r.json()
            if 'result' in json_data:
                result = json_data['result']
                block_height = result.get('sync_info', {}).get('latest_block_height', 'N/A')
                return block_height
    except Exception as e:
        print(e)
        return "Error to get network status"
    return -1


def fetch_validators_data(validator_address):
    try:
        fetch_url = 'https://api.nodejom.xyz/validators'
        headers = {
            "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpYXQiOjE3MDcwODQzNjMsImV4cCI6MTcxNzQ1MjM2M30.4Fk2-GpkRKK7SiTN4AgpmLUWUGTidBDYcIe-U_tacaE"}
        fetch_response = requests.get(fetch_url, headers=headers)
        if fetch_response.status_code == 200:
            more_data = fetch_response.json().get('data')
            data_string = f"""```
Unable to find information about your validator {validator_address}, make sure you have bonded and wait after 2 epochs then try again.
            ```"""
            for validator in more_data.get('validators'):
                if validator["address_hex"] == validator_address:
                    address = validator["address"]
                    moniker = validator["moniker"]
                    tokens = validator["tokens"]
                    status = validator["status"]
                    if len(moniker.strip()) == 0:
                        moniker = "N/A"
                    data_string = f"""```
Validator status\n
Address              : {address}
Address hex          : {validator_address}
Moniker              : {moniker}
Bonded amount        : {tokens}
Status               : {status}
        ```"""

            return data_string
        else:
            return "Cannot fetch data of validator"
    except Exception as e:
        print(e)
        return "Error to get validator status"


def get_votes():
    try:
        response = requests.get("https://it.api.namada.red/api/v1/chain/governance/proposals")
        # Parse the JSON response
        data = response.json()
        # Loop over all proposals
        voting_proposals = []
        for proposal in data["proposals"]:
            # Check if the result is "VotingPeriod"
            if proposal["result"] == "VotingPeriod":
                voting_proposals.append(proposal)

        voting_proposals = sorted(voting_proposals, key=lambda x: x['id'], reverse=True)

        response_message = '```Voting Period \n'
        for proposal in voting_proposals:
            response_message += f"{proposal['id']} {proposal['kind']} {proposal['author']['Account']} {proposal['start_epoch']}/{proposal['end_epoch']}/{proposal['grace_epoch']}\n"
        response_message += '```'
        return response_message
    except Exception as e:
        print(e)
        return "Error to get proposals"


def get_top_list(type):
    try:
        connection = db.create_connection()
        top_list = db.get_player_by_number(conn=connection, number=30, type=type)
        response_message = f'```Top 30 {type} \n\n'
        for player in top_list:
            id = player[0]
            last_20_chars = "..." + id[-10:]
            moniker = player[1]
            score = player[2]
            formatted_number = "{:,}".format(score)
            formatted_number = formatted_number.replace(",", ".")
            ranking_position = player[3]
            response_message += f"#{ranking_position} {moniker} {formatted_number} {last_20_chars}\n"
        response_message += '```'
        print(response_message)
        connection.close()
        return response_message
    except Exception as e:
        print(e)
        return "Error to get top 100"


def get_point(public_key):
    try:
        connection = db.create_connection()
        top_list = db.get_player_by_id_or_moniker(conn=connection, id=public_key)
        response_message = f'```NEBB info \n\n'
        count = len(top_list)
        if count > 0:
            for player in top_list:
                id = player[0]
                last_20_chars = "..." + id[-10:]
                moniker = player[1]
                score = player[2]
                formatted_number = "{:,}".format(score)
                formatted_number = formatted_number.replace(",", ".")
                ranking_position = player[3]
                response_message += f"#{ranking_position} {moniker} {formatted_number} {last_20_chars}\n"
        else:
            response_message += f"Unable to find info about your public key ."
        response_message += '```'
        print(response_message)
        connection.close()
        return response_message
    except Exception as e:
        print(e)
        return "Error to get top 100"


@client.on(events.NewMessage(pattern='/start'))
async def start_handler(event):
    global QUERY
    QUERY = EMPTY
    msg = '''
/network - Get network status 
/validator - Get validator status
/my_validator - Get your validator status 
/update_my_validator - Update your validator
/disable_update - You will not receive automatic notifications about your validator and proposals.
/proposals - Get list proposals are activating
/top30 - Get top 30 NEBB 
/point - Get current NEBB point'''
    await event.respond(msg)


@client.on(events.NewMessage(pattern='/network'))
async def start_handler(event):
    global QUERY
    QUERY = EMPTY
    msg = get_network_status()
    await event.respond(msg)


@client.on(events.NewMessage(pattern='/validator'))
async def start_handler(event):
    msg = """Please enter validator address:"""
    await event.respond(msg)


@client.on(events.NewMessage(pattern='/my_validator'))
async def start_handler(event):
    conn = db.create_connection()
    user = db.get_user_by_id(conn, event.peer_id.user_id)
    db.close_connection(conn)
    if len(user) == 0:
        msg = """Please enter your validator address:"""
        await event.respond(msg)
    else:
        global QUERY
        QUERY = EMPTY
        await event.respond("loading your validator....")
        msg = fetch_validators_data(user[0][0])
        await event.respond(msg)


@client.on(events.NewMessage(pattern='/update_my_validator'))
async def start_handler(event):
    msg = """Please enter your new validator address:"""
    await event.respond(msg)


@client.on(events.NewMessage(pattern='/disable_update'))
async def start_handler(event):
    global QUERY
    QUERY = EMPTY
    conn = db.create_connection()
    db.delete_user(conn, event.peer_id.user_id)
    db.close_connection(conn)
    msg = """You have successfully disabled automatic notifications about validator and proposals."""
    await event.respond(msg)


@client.on(events.NewMessage(pattern='/proposals'))
async def start_handler(event):
    global QUERY
    QUERY = EMPTY
    await event.respond("loading active proposals...")
    msg = get_votes()
    await event.respond(msg)


@client.on(events.NewMessage(pattern='/top30'))
async def start_handler(event):
    global QUERY
    QUERY = EMPTY
    await event.respond("loading top 100...")
    msg = get_top_list("pilot")
    await event.respond(msg)
    msg = get_top_list("crew")
    await event.respond(msg)


@client.on(events.NewMessage(pattern='/point'))
async def start_handler(event):
    msg = """Please enter public key or moniker :\n
"""
    await event.respond(msg)


@client.on(events.NewMessage())
async def start_handler(event):
    global QUERY
    message = event.message.message
    print("QUERY : " + QUERY)
    print("message: " + message)
    print("----")
    if QUERY != EMPTY:
        if QUERY == CMD_VALIDATOR:
            await event.respond("loading validator info...")
            QUERY = EMPTY
            message = event.message.message
            message = message.replace(CMD_VALIDATOR, "")
            message = message.strip()
            if message and len(message) == 40:
                msg = fetch_validators_data(message)
                await event.respond(msg)
            else:
                await event.respond("Validator address is incorrect !")
        elif QUERY == CMD_POINT:
            await event.respond("loading your info...")
            QUERY = EMPTY
            message = event.message.message
            message = message.replace(CMD_POINT, "")
            message = message.strip()
            msg = get_point(message)
            await event.respond(msg)

        elif QUERY == CMD_UPDATE_MY_VALIDATOR or QUERY == CMD_MY_VALIDATOR:
            QUERY = EMPTY
            message = event.message.message
            message = message.replace(CMD_UPDATE_MY_VALIDATOR, "")
            message = message.strip()
            if message and len(message) == 40:
                user_id = event.peer_id.user_id
                connection = db.create_connection()
                db.save_user_table(conn=connection, data=(user_id, message,))
                connection.close()
                await event.respond(
                    "Your validator address has been updated !")
            else:
                await event.respond("Validator address is incorrect !")

    else:
        if message == CMD_VALIDATOR or message == CMD_POINT or message == CMD_MY_VALIDATOR \
                or message == CMD_UPDATE_MY_VALIDATOR:
            print("QUERY = message = " + message)
            QUERY = message
        else:
            QUERY = EMPTY


with client.start(bot_token=bot_token):
    db.main()
    print("Start send_vote_updates!")
    client.loop.create_task(check_block_validator_interval(600, client))  # 600 seconds = 10 minutes
    client.loop.create_task(send_validator_updates_interval(21600, client))  # 21600 seconds = 6hrs
    client.loop.create_task(send_vote_updates_interval(43200, client))  # 43200 seconds = 12hrs
    client.loop.create_task(fetch_point_updates_interval(3600))  # 3600 seconds = 1hrs
    print("Start namada bot!")

    client.run_until_disconnected()
