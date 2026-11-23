import httpx

class OllamaConnectionError(Exception):
    pass


class OllamaTimeoutError(Exception):
    pass


async def generate_response(messages: list[dict[str, str]]) -> str:

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:11434/api/chat",
                json={
                    "model": "qwen2.5:3b",
                    "messages": messages,
                    "stream": False,
                },
                timeout=120.0,
            )

        response.raise_for_status()

    except httpx.ConnectError as exc:
        raise OllamaConnectionError("Unable to connect to Ollama") from exc

    except httpx.TimeoutException as exc:
        raise OllamaTimeoutError("Ollama request timed out") from exc

    return response.json()["message"]["content"]