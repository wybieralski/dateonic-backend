import psycopg2

def test_connection():
    try:
        conn = psycopg2.connect(
            dbname="dateonic",
            user="postgres",
            password="smc7bp59",
            host="localhost",
            port="5432"
        )
        print("Połączenie udane!")
        conn.close()
    except Exception as e:
        print(f"Błąd połączenia: {e}")

test_connection()