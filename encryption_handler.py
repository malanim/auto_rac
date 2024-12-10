import json
import base64
import os
from hashlib import sha256

def xor_encrypt(input_string, key):
    """Функция для шифрования данных с использованием XOR."""
    key = key.encode()
    input_string = input_string.encode()
    key_length = len(key)
    output = bytearray()
    
    for i in range(len(input_string)):
        output.append(input_string[i] ^ key[i % key_length])
    
    return base64.b64encode(output).decode()

def xor_decrypt(encrypted_string, key):
    """Функция для дешифрования данных с использованием XOR."""
    encrypted_bytes = base64.b64decode(encrypted_string)
    key = key.encode()
    key_length = len(key)
    output = bytearray()
    
    for i in range(len(encrypted_bytes)):
        output.append(encrypted_bytes[i] ^ key[i % key_length])
    
    return output.decode()

class EncryptionHandler:
    def __init__(self, json_file, login=None, password=None):
        self.json_file = json_file
        self.login = login
        self.password = password
        self.key = self._get_key()

    def _get_key(self):
        if self.password:
            password_hash = sha256(self.password.encode()).hexdigest()
            return password_hash
        return None

    def register_user(self, login, password):
        if self.user_exists(login):
            return False
        password_hash = self._hash_password(password)
        self._save_user(login, password_hash)
        return True

    def authenticate_user(self, login, password):
        if self._verify_password(login, password):
            self.login = login
            self.password = password
            self.key = self._get_key()
            return True
        else:
            return False

    def user_exists(self, login):
        with open(self.json_file, 'r') as f:
            data = json.load(f)
        return login in data.get('users', {})

    def _hash_password(self, password):
        import hashlib
        return hashlib.sha256(password.encode()).hexdigest()

    def _save_user(self, login, password_hash):
        try:
            with open(self.json_file, 'r') as f:
                data = json.load(f)
        except FileNotFoundError:
            data = {}

        if 'users' not in data:
            data['users'] = {}

        data['users'][login] = password_hash
        
        with open(self.json_file, 'w') as f:
            json.dump(data, f)

    def _verify_password(self, login, password):
        with open(self.json_file, 'r') as f:
            data = json.load(f)
        
        if login in data.get('users', {}):
            stored_password_hash = data['users'][login]
            return stored_password_hash == self._hash_password(password)
        return False

    def encrypt(self, data, name):
        if not self.key:
            raise ValueError("Сначала выполните аутентификацию.")
        encrypted_data = xor_encrypt(data, self.key)
        with open(self.json_file, 'r') as f:
            data = json.load(f)
        
        if self.login not in data:
            data[self.login] = {}
        
        data[self.login][name] = encrypted_data
        
        with open(self.json_file, 'w') as f:
            json.dump(data, f)
        
        return encrypted_data

    def decrypt(self, name):
        if not self.key:
            raise ValueError("Сначала выполните аутентификацию.")
        with open(self.json_file, 'r') as f:
            data = json.load(f)
        
        if self.login in data and name in data[self.login]:
            encrypted_data = data[self.login][name]
            decrypted_data = xor_decrypt(encrypted_data, self.key)
            
            return decrypted_data
        else:
            raise ValueError(f"Name '{name}' not found for login '{self.login}' in the JSON file.")

    def get_all_encrypted_data(self):
        if not self.key:
            raise ValueError("Сначала выполните аутентификацию.")
        with open(self.json_file, 'r') as f:
            data = json.load(f)
        
        if self.login in data:
            return data[self.login]
        else:
            return {}

    def delete_data(self, name):
        if not self.key:
            raise ValueError("Сначала выполните аутентификацию.")
        with open(self.json_file, 'r') as f:
            data = json.load(f)
        
        if self.login in data and name in data[self.login]:
            del data[self.login][name]
            with open(self.json_file, 'w') as f:
                json.dump(data, f)
            return True
        else:
            return False

    def update_data(self, name, new_data):
        if not self.key:
            raise ValueError("Сначала выполните аутентификацию.")
        with open(self.json_file, 'r') as f:
            data = json.load(f)
        
        if self.login in data and name in data[self.login]:
            encrypted_data = xor_encrypt(new_data, self.key)
            data[self.login][name] = encrypted_data
            with open(self.json_file, 'w') as f:
                json.dump(data, f)
            return True
        else:
            return False
