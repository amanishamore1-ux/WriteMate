import requests
import json

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "kimi-k2.5:cloud"

# ================= NORMAL (KEEP THIS AS IS) =================
def generate_blog(prompt):
    try:
        response = requests.post(OLLAMA_URL, json={
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False
        })

        result = response.json()
        print("OLLAMA RESPONSE:", result)

        if "response" in result:
            return result["response"]

        if "error" in result:
            return f"⚠ AI Error: {result['error']}"

        return "⚠ AI failed to generate content. Try again."

    except Exception as e:
        return f"⚠ Server Error: {str(e)}"


# ================= STREAMING (NEW) =================
def generate_blog_stream(prompt):
    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL_NAME,
                "prompt": prompt,
                "stream": True  # 🔥 ENABLE STREAMING
            },
            stream=True
        )

        for line in response.iter_lines():
            if line:
                try:
                    data = json.loads(line.decode("utf-8"))

                    if "response" in data:
                        yield data["response"]

                except Exception:
                    continue

    except Exception as e:
        yield f"\n⚠ Error: {str(e)}"