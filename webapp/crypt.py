from urllib import urlencode
from urlparse import parse_qsl
# from simplecrypt import encrypt, decrypt
from base64 import b64encode, b64decode

from Crypto.Cipher import AES

IV = 16 * '\x00'

def encrypt(text, key):
    text += '\0' * (16 - len(text) % 16)
    encryptor = AES.new(key, AES.MODE_CBC, IV=IV)
    return encryptor.encrypt(text)

def decrypt(ciphertext, key):
    decryptor = AES.new(key, AES.MODE_CBC, IV=IV)
    return decryptor.decrypt(ciphertext).strip('\0')

def encrypt_creds(creds, key):
    return b64encode(encrypt(urlencode(creds), key))

def decrypt_creds(encrypted_creds, key):
    return dict(parse_qsl(decrypt(b64decode(encrypted_creds), key)))

if __name__ == '__main__':
    creds = encrypt_creds(dict(username='eli', password='pass'), key='0123456789abcdef')
    print creds
    print decrypt_creds(creds, key='0123456789abcdef')
