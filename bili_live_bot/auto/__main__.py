from auto import *
import json
import asyncio

with open("./config.json") as f:
    config = json.load(f)

ds = DanmakuSpider(config["room_id"])
ls = LiveSpider(config["bili_cookies"], config["room_id"])
aic = OpenAIConnector(config["openai_api_key"], config["preset_prompts"])
# uncomment if you need to listen on room
# em = EchoMonitor()
# ds.register(em)
gpt = GPTMonitor(config["uid"], aic, ls)

ds.register(gpt)
ls.start()

loop = asyncio.get_event_loop()
loop.run_until_complete(ds.start())
loop.close()