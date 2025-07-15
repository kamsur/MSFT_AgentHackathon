import os
from openai import AzureOpenAI

endpoint = os.getenv("PROJECT_ENDPOINT", "https://hackathon-group6-123.services.ai.azure.com")
model_name = os.getenv("MODEL_DEPLOYMENT_NAME", "gpt-4.1")
deployment = os.getenv("MODEL_DEPLOYMENT_NAME", "gpt-4.1")

subscription_key = os.getenv("SUBSCRIPTION_KEY", "ApkSH2yYEJr03QypDtkp7K6ub2Zd4FCEntVvUCPs68uzmDvyYpYdJQQJ99BGACYeBjFXJ3w3AAAAACOGauXV")

api_version = os.getenv("API_VERSION", "2024-12-01-preview")

client = AzureOpenAI(
    api_version=api_version,
    azure_endpoint=endpoint,
    api_key=subscription_key,
)

response = client.chat.completions.create(
    messages=[
        {
            "role": "system",
            "content": "You are a helpful assistant.",
        },
        {
            "role": "user",
            "content": "I am going to Paris, what should I see?",
        }
    ],
    max_completion_tokens=800,
    temperature=1.0,
    top_p=1.0,
    frequency_penalty=0.0,
    presence_penalty=0.0,
    model=deployment
)

print(response.choices[0].message.content)