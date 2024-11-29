import requests


def test_analyze_endpoint():
    url = "http://localhost:8000/api/analyze"

    try:
        # Otwieramy plik testowy i dodajemy więcej informacji debugowych
        print("Opening test file...")
        with open('test.csv', 'rb') as f:
            files = {
                'file': ('test.csv', f, 'text/csv')
            }

            print("Sending request...")
            response = requests.post(url, files=files)

            print(f"Response status code: {response.status_code}")
            print(f"Response headers: {response.headers}")

            try:
                print(f"Response content: {response.json()}")
            except:
                print(f"Raw response content: {response.content}")

            if response.status_code != 200:
                print(f"Error details: {response.text}")

    except FileNotFoundError:
        print("Error: test.csv file not found!")
    except Exception as e:
        print(f"Unexpected error: {str(e)}")


if __name__ == "__main__":
    test_analyze_endpoint()