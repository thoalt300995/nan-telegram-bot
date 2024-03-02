
## Namada telegram bot

### Command
```
/network - Get network status 
/validator - Get validator status
/my_validator - Get your validator status
/proposals - Get list proposals are activating
/top100 - Get top 100 NEBB 
/point - Get current NEBB point by input validator address or moniker name
/update_my_validator - Update your validator
/disable_update - You will not receive automatic notifications about your validator and proposals.

```

### Features:

- Check network status
```
Network Name       : shielded-expedition.88f17d1d14
Current epoch      : 23
Block Height       : 90044
Last Time Update   : 2 days ago
```
- Check validator status
```
Address              : tnam1q9k0jkssxmwdd0g3vpulvl7yp3rv7rnnuyezutcp
Address hex          : 2C8300C6D4EE7F9641963DF7B7F53391CC172CB0
Moniker              : N/A
Bonded amount        : 2692877.3
Status               : active
```
- List proposals are activing
```
Proposals are currently in the voting stage: 

Update time (UTC): 2024-03-02 02:15:26 
260 PgfFunding tnam1qqnarl4h6dsy4jchy0tcxakh286ec03weyfnks6e 22/24/26
259 PgfFunding tnam1qzg7975ktktcpm4x6xz9zt0ltpc29aq86qf9k9w5 22/24/26
258 PgfSteward tnam1qxgnegx3se9htr05982atux3ytr797s8av39s5vy 22/24/26
257 PgfSteward tnam1qzuz70pvwhc64wq7uquuayggcjhnmm5vsgjre2p7 22/26/28
256 PgfSteward tnam1qxt9tr3ctrhnxa5pa70uj2yclh5edlq6avm3pzfc 22/24/27
254 PgfSteward tnam1qzlgjda3ne3a8jfawhlg5nujjwv923srfch85mts 22/26/28
252 PgfSteward tnam1qzxectrfqkggtjdjnvydeas7lfhfurh08qapsz73 22/24/26
...
```
- Monitor validator ( bot will send status of validator each 6hrs)

```The bot will automatically check and send information about your validator every 6 hours.```

- Monitor proposals ( bot will send proposals are activing each 12hrs)

```The bot will check proposals in the voting stage and will automatically send you updates every 12 hours.```
- Monitor your validator uptime. The bot will check every 10 minutes and if you missed 10 blocks in the last 100 blocks, the bot will send you a warning message.

``` 
------ WARNING MISSED BLOCK ------

You validator : 2C8300C6D4EE7F9641963DF7B7F53391CC172CB0
Block missed  : 100

This is the number of blocks missed in the latest 100 blocks, check again in the next 10 minutes.

```
- View top 100 NEBB
```

Top 100 pilot 

#1 CroutonDigital 68.093.383.367 ...lz2y30dua2
#2 Citadel.one 39.324.363.288 ...73pj0eu26h
#3 Validatorade 36.405.799.864 ...xjlv62jzcq
#4 CryptoSJnet 9.928.331.967 ...wrzvjfujne
#5 StakeUp 9.655.125.959 ...ssesrw2et5
...

Top 100 crew 

#1 nobita 9.294.828.982 ...0tscskthm0
#2 Nancy2393622235 7.763.976.352 ...xplgquqlx9
#3 dimi 🦙 5.309.058.671 ...eku762p5ta
#4 thoale3009 5.173.620.995 ...qpy5qje5fv
#5 mangeonoca 3.421.730.425 ...39pwpl5up0
...

```
- Check NEBB point by address
```
#23 Suntzu 4.838.679.963 ...4t468cjvkg
```

- Update your validator, and you can also cancel automatic messages about validator and proposals from the bot.

## Install and run

```
git clone https://github.com/thoalt300995/nan-telegram-bot.git
cd nan-telegram-bot
pip3 install telethon
pip3 install python-dotenv

cp .env.sample .env

# Change value in .env file
# Run
python3 main.py
```
