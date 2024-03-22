# Bili Live Bot
provides
1. A simple way to monitor real-time danmakus of any Bilibili live room (no need for authorization).
2. A simple way to send danmakus in any Bilibili live room (authorization required).
3. A simple access to OpenAI (either with or without an openai api key).

For ChatGPT connection, you can either use the `OpenAIConnector` with an API key, or the `ChatGPTDriver`. The latter will use the session cookies provided by the user.

All spiders are implemented as `Observer` design pattern, so you can easily add your own spiders to monitor other events and register callbacks. Surprisingly, with our spiders, you can send danmakus with no limit (no maximum danmaku rate and words)!

NOTE: This bot is based on spiders, not the official Bilibili API (which requires developer authorization), so it may not be as stable as the official API. Overuse of it may lead to Bilbili's anti-spider mechanism, so use it with caution.

NOTE: This bot is for educational purposes only. Please respect the rules of the Bilibili platform and do not use it for malicious purposes.

To use this bot, you need to install the following packages:
