import os
from firebase_admin import credentials

cred_path = './credentials/firebase_admin_sdk.json'
print(f"Checking path: {cred_path}")
print(os.path.exists(cred_path))  # Ini harus mencetak True jika file ada

if not os.path.exists(cred_path):
    raise FileNotFoundError(f"Path to the credentials file is incorrect: {cred_path}")

cred = credentials.Certificate(cred_path)
print("Credentials loaded successfully")