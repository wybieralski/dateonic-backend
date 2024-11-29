from openai import OpenAI
from dotenv import load_dotenv
import os

# Załaduj zmienne środowiskowe
load_dotenv()


def test_gpt_connection():
    try:
        # Inicjalizacja klienta OpenAI
        client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

        # Prosty prompt testowy
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "user", "content": "Return exactly this JSON: {\"test\": \"successful\"}"}
            ]
        )

        # Wyświetl odpowiedź
        print("Status: Connection successful")
        print(f"Response: {response.choices[0].message.content}")

    except Exception as e:
        print(f"Error: {str(e)}")


if __name__ == "__main__":
    test_gpt_connection()