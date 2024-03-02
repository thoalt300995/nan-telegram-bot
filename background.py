import concurrent
import time
import asyncio
import requests
import db


async def send_vote_updates(client):
    print("=> start check voting and send message to all users")
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

        currentTime = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
        message = '```Proposals are currently in the voting stage: \n\n'
        message += f"Update time (UTC): {currentTime} \n"
        for proposal in voting_proposals:
            message += f"{proposal['id']} {proposal['kind']} {proposal['author']['Account']} {proposal['start_epoch']}/{proposal['end_epoch']}/{proposal['grace_epoch']}\n"
        message += '```'

        conn = db.create_connection()
        users = db.get_all_user(conn)
        db.close_connection(conn)
        for user in users:
            user = await client.get_entity(user[0])
            await client.send_message(user, message)
        print("Send voting ended!")
    except Exception as e:
        print(e)


async def fetch_validators_data(client):
    try:
        conn = db.create_connection()
        fetch_url = 'https://api.nodejom.xyz/validators'
        headers = {
            "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpYXQiOjE3MDcwODQzNjMsImV4cCI6MTcxNzQ1MjM2M30.4Fk2-GpkRKK7SiTN4AgpmLUWUGTidBDYcIe-U_tacaE"}
        fetch_response = requests.get(fetch_url, headers=headers)
        if fetch_response.status_code == 200:
            more_data = fetch_response.json().get('data')
            for validator in more_data.get('validators'):
                validator_address = validator["address_hex"]
                user_id = db.get_user_by_validator(conn, validator["address_hex"])
                if len(user_id) > 0:
                    address = validator["address"]
                    moniker = validator["moniker"]
                    tokens = validator["tokens"]
                    status = validator["status"]
                    if len(moniker.strip()) == 0:
                        moniker = "N/A"

                    currentTime = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
                    message = f"""```
Validator status\n\n
Update time (UTC)    : {currentTime}
Address              : {address}
Address hex          : {validator_address}
Moniker              : {moniker}
Bonded amount        : {tokens}
Status               : {status}
        ```"""

                    user = await client.get_entity(user_id[0][0])
                    await client.send_message(user, message)
    except Exception as e:
        print(e)


# Fetch data
def fetch_pilot_page(page):
    conn = db.create_connection()
    try:
        print("start request pilot page : " + str(page))
        response = requests.get(f"https://it.api.namada.red/api/v1/scoreboard/pilots?page={page}",
                                timeout=1000)
        data = response.json()
        if len(data["players"]) == 0 or data['players'][0]['score'] == 0:
            return

        for player in data['players']:
            player_id = player['id']
            moniker = player['moniker']
            score = player['score']
            ranking_position = player['ranking_position']
            # assuming the type is always 'pilot' as per your api endpoint
            type = 'pilot'
            db.save_ranking_table(conn, (player_id, moniker, score, ranking_position, type))

        page += 1
        time.sleep(30)
    except requests.exceptions.Timeout:
        print("The request timed out")
    except Exception as e:
        print(e)
        print(f"An error occurred: {e}")

    conn.close()


def get_missed_block(validator):
    try:
        response = requests.get(
            f"https://namada-explorer-api.stakepool.dev.br/node/validators/validator/{validator}", timeout=60)
        data = response.json()

        count_missed_block = 0
        for uptime in data['uptime']:
            sign_status = uptime["sign_status"]
            if sign_status is False:
                count_missed_block += 1

        return count_missed_block
    except Exception as e:
        print(f"An error get_missed_block : {e}")


async def check_validator_uptime(client):
    try:
        print("Start check uptime validator !")
        conn = db.create_connection()
        users = db.get_all_user(conn)
        db.close_connection(conn)
        for user in users:
            id = user[0]
            validator = user[1]
            count_missed_block = get_missed_block(validator)
            if count_missed_block > 10:
                message = f"""```  ------ WARNING MISSED BLOCK ------\n
You validator : {validator}
Block missed  : {count_missed_block}

This is the number of blocks missed in the latest 100 blocks, check again in the next 10 minutes.
```"""
                user = await client.get_entity(id)
                await client.send_message(user, message)
        print("Check uptime validator ended !")
    except Exception as e:
        print(f"An error check_uptime : {e}")


def fetch_crew_page(page):
    conn = db.create_connection()
    try:
        print("request crew page : " + str(page))
        response = requests.get(f"https://it.api.namada.red/api/v1/scoreboard/crew?page={page}", timeout=2000)
        data = response.json()
        if len(data["players"]) == 0 or data['players'][0]['score'] == 0:
            return

        for player in data['players']:
            player_id = player['id']
            moniker = player['moniker']
            score = player['score']
            ranking_position = player['ranking_position']
            type = 'crew'
            db.save_ranking_table(conn, (player_id, moniker, score, ranking_position, type))

        page += 1
        time.sleep(30)
    except Exception as e:
        print(f"An error occurred: {e}")
    conn.close()


def start_fetch_point():
    num_pages_to_request = 12
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        pages = list(range(0, num_pages_to_request))
        executor.map(fetch_pilot_page, pages)

    num_pages_to_request = 30
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        pages = list(range(0, num_pages_to_request))
        executor.map(fetch_crew_page, pages)


async def fetch_point_updates_interval(interval):
    while True:
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, start_fetch_point)
        await asyncio.sleep(interval)  # pause for the interval time


async def send_vote_updates_interval(interval, client):
    await asyncio.sleep(interval)  # pause for the interval time
    while True:
        await send_vote_updates(client)
        await asyncio.sleep(interval)  # pause for the interval time


async def send_validator_updates_interval(interval, client):
    await asyncio.sleep(interval)  # pause for the interval time
    while True:
        await fetch_validators_data(client)
        await asyncio.sleep(interval)  # pause for the interval time


async def check_block_validator_interval(interval, client):
    await asyncio.sleep(interval)  # pause for the interval time
    while True:
        await check_validator_uptime(client)
        await asyncio.sleep(interval)  # pause for the interval time
