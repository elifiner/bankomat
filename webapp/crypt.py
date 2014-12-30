from urllib import urlencode
from urlparse import parse_qsl
from base64 import b64encode, b64decode

from Crypto.Cipher import AES

IV = 16 * '\x00'

def encrypt(key, text):
    text += '\0' * (16 - len(text) % 16)
    encryptor = AES.new(key, AES.MODE_CBC, IV=IV)
    return encryptor.encrypt(text)

def decrypt(key, ciphertext):
    decryptor = AES.new(key, AES.MODE_CBC, IV=IV)
    return decryptor.decrypt(ciphertext).strip('\0')

def encrypt_dict(key, dict):
    return b64encode(encrypt(key, urlencode(dict)))

def decrypt_dict(key, ciphertext):
    return dict(parse_qsl(decrypt(key, b64decode(ciphertext))))

if __name__ == '__main__':
    key = '0123456789abcdef'
    creds = encrypt_dict(key, dict(username='eli', password='pass'))
    print creds
    print decrypt_dict(key, creds)
