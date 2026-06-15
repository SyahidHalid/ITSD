# buat API
# https://openrouter.ai/workspaces/default/keys

# 1 day API key
# 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

# cari LLM yg free
# OpenAI: gpt-oss-120b (free)
# https://openrouter.ai/openai/gpt-oss-120b:free#providers
# openai/gpt-oss-120b:free

# pip install openai --trusted-host pypi.org --trusted-host files.pythonhosted.org

import httpx
from openai import OpenAI

# Create httpx client with SSL verification disabled
http_client = httpx.Client(
    verify=False  # ⚠️ disables SSL certificate validation
)

# Initialize OpenAI client with OpenRouter base URL
client = OpenAI(
    api_key="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",
    base_url="https://openrouter.ai/api/v1",
    http_client=http_client  # ✅ inject custom client
)

# Make request
completion = client.chat.completions.create(
    model="openai/gpt-oss-120b:free",
    messages=[
        {
            "role": "user",
            "content": "What is the meaning of life?"
        }
    ],
    extra_headers={
        "HTTP-Referer": "https://your-site.com",
        "X-Title": "your-site-name",
    }
)

# Print response
print(completion.choices[0].message.content)




