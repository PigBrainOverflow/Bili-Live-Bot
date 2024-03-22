import bs4
from collections import namedtuple
from .OpenAIConnector import *
from .LiveSpider import *

DanmakuInfo = namedtuple("DanmakuInfo", ["uname", "uid", "ts", "data"])

class Monitor:
    def __init__(self):
        pass

    async def update(self, args: bs4.BeautifulSoup | Exception):
        pass

class EchoMonitor(Monitor):
    def __init__(self):
        super().__init__()

    async def update(self, args: bs4.BeautifulSoup | Exception):
        if isinstance(args, Exception):
            print("Error!")
        else:
            print(args.text)

class GPTMonitor(Monitor):
    _current_ts: str    # data-ts is the timestamp of sending
    _current_response: str  # the response to the last danmaku
    _uid: str   # self uid
    _openai_connector: OpenAIConnector
    _live_spider: LiveSpider

    @staticmethod
    def get_attr_with_default(elem, name: str, default_val=None) -> str | None:
        if name in elem.attrs:
            return elem.attrs[name]
        else:
            return default_val

    def __init__(self, uid: str, openai_connector: OpenAIConnector, live_spider: LiveSpider):
        super().__init__()
        self._current_ts = ""
        self._current_response = ""
        self._uid = uid
        self._openai_connector = openai_connector
        self._live_spider = live_spider

    async def update(self, args: bs4.BeautifulSoup | Exception):
        if isinstance(args, Exception):
            print("Error!")
        else:
            danmakus = [
                DanmakuInfo(
                    GPTMonitor.get_attr_with_default(danmaku, "data-uname"),
                    GPTMonitor.get_attr_with_default(danmaku, "data-uid"),
                    GPTMonitor.get_attr_with_default(danmaku, "data-ts"),
                    GPTMonitor.get_attr_with_default(danmaku, "data-danmaku")
                )
                for danmaku in args.div.find_all("div", class_="chat-item", recursive=False)
                if "data-uid" in danmaku.attrs and danmaku.attrs["data-uid"] != self._uid  # otherwise it's a system message or my own message
            ]
            # choose the most recent danmaku (with the largest data-ts)
            try:
                danmaku = max(danmakus, key=lambda x: x.ts)
                if danmaku.ts > self._current_ts and danmaku.data in self._current_response:    # if it's not the echo of the last response
                    self._current_ts = danmaku.ts
                    # send to openai
                    print("New danmaku: " + danmaku.data)
                    response = await self._openai_connector.query(danmaku.data)
                    print("Response: " + response)
                    # send to live
                    await self._live_spider.send_long_danmaku(response)
                    self._current_response = response
                    await asyncio.sleep(2)
            except ValueError:
                # no recent danmaku
                pass


if __name__ == "__main__":
    import json
    with open("./config.json", "r") as f:
        config = json.load(f)
    from .DanmakuSpider import *
    ds = DanmakuSpider(config["room_id"])
    gpt = GPTMonitor(config["uid"], None, None)
    ds.register(gpt)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(ds.start())
    loop.close()

