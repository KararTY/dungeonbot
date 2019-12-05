import re
import time
import threading

import emoji
import requests

import auth
import utility as util
import commands as cmd
import database as opt
import schemes

db = opt.MongoDatabase

closed = 1

def livecheck():
    while True:
        headers = { 'Client-ID': auth.clientID }
        params = (('user_login', auth.channeluser),)
        response = requests.get('https://api.twitch.tv/helix/streams', headers=headers, params=params).json()
        if not response['data']:
            db(opt.DUNGEONS).update_one(0, { '$set': { 'open': 1 } })
        else:
            db(opt.DUNGEONS).update_one(0, { '$set': { 'open': 0 } })
        time.sleep(5)

livecheckthread = threading.Thread(target = livecheck)
livecheckthread.start()

util.start()

while True:
    resp = emoji.demojize(util.sock.recv(2048).decode('utf-8'))

    print(resp)

    if resp.startswith('PING'):
        util.pong()

    elif len(resp) > 0:
        username = re.search('display-name=(.+?);', resp)
        if username:
            username = username.group(1)
        message = re.search(r':(.*)\s:(.*)', resp)
        if message:
            message = message.group(2).strip()
            if db(opt.DUNGEONS).find_one_by_id(0)['open'] == 1:

                if util.floodcounter == 0:

                    if (message == '+commands' or message == '+help'):
                        cmd.commands()

                    if message == '+enterdungeon':
                        cmd.enterdungeon(username, message)

                    if (message == '+dungeonlvl' or message == '+dungeonlevel'):
                        cmd.dungeonlvl()

                    if message == '+dungeonmaster':
                        cmd.dungeonmaster()

                    if message == '+dungeonstats':
                        cmd.dungeonstats()

                    if message == '+dungeonstatus':
                        cmd.dungeonstatus()

                    if (message == '!ping' or message == '+ping'):
                        cmd.ping()

                    if message == '+register':
                        cmd.register(username)

                    if (message.startswith('+xp') or message.startswith('+exp')):
                        cmd.userexperience(username, message)

                    if (message.startswith('+lvl') or message.startswith('+level')):
                        cmd.userlevel(username, message)

                    if message.startswith('+winrate'):
                        cmd.winrate(username, message)

            if message.startswith('+tag'):
                util.usertag(username, message)

            if message == '+resetcd':
                util.resetcd(username)

            if message == '+restart':
                util.restart(username)
