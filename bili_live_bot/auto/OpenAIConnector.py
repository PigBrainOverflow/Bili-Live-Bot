import openai_async
import json


class OpenAIConnector:
    _openai_api_key: str
    _preset_prompts: dict

    def __init__(self, openai_api_key: str, preset_prompts: dict):
        self._openai_api_key = openai_api_key
        self._preset_prompts = preset_prompts

    async def query(self, prompt: str) -> str:
        try:
            response = await openai_async.chat_complete(
                self._openai_api_key,
                timeout=4,
                payload={
                    "model": "gpt-3.5-turbo",
                    "max_tokens": 20,
                    "messages": [
                        self._preset_prompts,
                        {"role": "user", "content": prompt}
                    ]
                }
            )
            if response.status_code != 200:
                return f"Error: {response.status_code}"
            return response.json()["choices"][0]["message"]["content"]
        except TimeoutError as toe:
            return f"Error: {toe} - Timeout"


if __name__ == "__main__":
    import asyncio
    with open("./config.json") as f:
        config = json.load(f)

    gpt = OpenAIConnector(config["openai_api_key"], config["preset_prompts"])
    response = asyncio.run(gpt.query("Do you like programming?"))
    print(response)