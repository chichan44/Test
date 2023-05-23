#!/usr/bin/env python3
# Simple Discord SelfBot
# Created By Viloid ( github.com/vsec7 )
# Use At Your Own Risk

#Update log

# - Add random channel, so message will be send to random channel
# - Add random delay to avoid detection better

#Plan

# - Refactor
# - Sticker send instead of message
# - Send random sticker to random channel after execute main function x times

import requests, random, sys, yaml, codecs, time
from random import randint
from time import sleep

class Discord:

    def __init__(self, t):
        self.base = "https://discord.com/api/v9"
        self.auth = { 'authorization': t }
        
    def getMe(self):
        u = requests.get(self.base + "/users/@me", headers=self.auth).json()
        return u
        
    def getMessage(self, cid, l):
        u = requests.get(self.base + "/channels/" + str(cid) + "/messages?limit=" + str(l), headers=self.auth).json()
        return u
        
    def sendMessage(self, cid, txt):    
        u = requests.post(self.base + "/channels/" + str(cid) + "/messages", headers=self.auth, json={ 'content': txt }).json()
        return u

    def replyMessage(self, cid, mid, txt):    
        u = requests.post(self.base + "/channels/" + str(cid) + "/messages", headers=self.auth, json={ 'content': txt, 'message_reference': { 'message_id': str(mid) } }).json()
        return u

    def deleteMessage(self, cid, mid):
        u = requests.delete(self.base + "/channels/" + str(cid) + "/messages/" + str(mid), headers=self.auth)
        return u

def quote():
    u = requests.get("https://raw.githubusercontent.com/lakuapik/quotes-indonesia/master/raw/quotes.min.json").json()
    return random.choice(list(u))['quote']

def simsimi(lc, txt):
    u = requests.post("https://api.simsimi.vn/v1/simtalk", data={ 'lc': lc, 'text': txt}).json()
    return u['message']
    
def random_channel(filename):
    with open(filename, 'r') as file:
        lines = file.readlines()
        random_line = random.choice(lines)
        return random_line.strip()
        
def randomsleep():
    # Generate a random delay between 1 and 5 seconds
    delay = random.uniform(10, 15)
    
    # Print the delay
    #print(f"Delay: {delay} seconds")
    
    # Pause execution for the generated delay
    #time.sleep(delay)
    return delay
    
    # Rest of your function code goes here

f = open("custom.txt")
text = f.read()      
text = text.replace('\\n','\n')

def main():
    with open('config.yaml') as cfg:
        conf = yaml.load(cfg, Loader=yaml.FullLoader)

    if not conf['BOT_TOKEN']:
        print("[!] Please provide discord token at config.yaml!")
        sys.exit()

    if not conf['CHANNEL_ID']:
        print("[!] Please provide channel id at config.yaml!")
        sys.exit()

    mode = conf['MODE']
    simi_lc = conf['SIMSIMI_LANG']
    delay = randint(62,64)
    del_after = conf['DEL_AFTER']
    repost_last = conf['REPOST_LAST_CHAT']
                
    if not mode: 
        mode = "quote"
        
    if not simi_lc:
        simi_lc = "id"
        
    if not repost_last: 
        repost_last = "100"
    
    while True:
        for token in conf['BOT_TOKEN']:
            try:

                for chan in conf['CHANNEL_ID']:
                    
                    Bot = Discord(token)
                    me = Bot.getMe()['username'] + "#" + Bot.getMe()['discriminator']
                    
                    if mode == "quote":
                        q = quote()
                        filename = "channelr.txt"
                        rc = random_channel(filename)
                        print(rc)
                        send = Bot.sendMessage(rc, q)
                        print("[{}][{}][QUOTE] {}".format(me, rc, q))
                        #sleep(randint(64,66))
                        #print()
                        if del_after:
                            
                            Bot.deleteMessage(rc, send['id'])
                            print("[{}][DELETE] {}".format(me, send['id']))
                            sleep(random_sleep())

                    elif mode == "repost":
                        res = Bot.getMessage(chan, random.randint(1,repost_last))
                        getlast = list(reversed(res))[0]                    
                        send = Bot.sendMessage(chan, getlast['content'])
                        print("[{}][{}][REPOST] {}".format(me, chan, getlast['content']))
                        if del_after:
                            
                            Bot.deleteMessage(chan, send['id'])
                            print("[{}][DELETE] {}".format(me, send['id']))
                        
                    elif mode == "simsimi":
                        res = Bot.getMessage(chan, "1")
                        getlast = list(reversed(res))[0]                
                        simi = simsimi(simi_lc, getlast['content'])

                        if conf['REPLY']:
                            send = Bot.replyMessage(chan, getlast['id'], simi)
                            print("[{}][{}][SIMSIMI] {}".format(me, chan, simi))
                        else:
                            send = Bot.sendMessage(chan, simi)
                            print("[{}][{}][SIMSIMI] {}".format(me, chan, simi))

                        if del_after:
                            
                            Bot.deleteMessage(chan, send['id'])
                            print("[{}][DELETE] {}".format(me, send['id']))

                    elif mode == "custom":
                        c = random.choice(open("custom.txt").readlines())
                        filename = "channelr.txt"
                        rc = random_channel(filename)
                        send = Bot.sendMessage(chan, c)
                        print("[{}][{}][CUSTOM] {}".format(me, chan, c))            
                        if del_after:
                            
                            Bot.deleteMessage(chan, send['id'])
                            print("[{}][DELETE] {}".format(me, send['id']))

            except Exception as e:
                print(e)
                #print(f"[Error] {token} : INVALID TOKEN / KICKED FROM GUILD!")
        
        print("-------[ Delay for {} seconds ]-------".format(randomsleep()))
        time.sleep(randomsleep())

if __name__ == '__main__':
    try:
        main()
    except Exception as err:
        print(f"{type(err).__name__} : {err}")
        