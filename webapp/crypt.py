from urllib import urlencode
from urlparse import parse_qsl
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

def encrypt_dict(dict, key):
    return b64encode(encrypt(urlencode(dict), key))

def decrypt_dict(ciphertext, key):
    return dict(parse_qsl(decrypt(b64decode(ciphertext), key)))

if __name__ == '__main__':
    creds = encrypt_dict(dict(username='eli', password='pass'), key='0123456789abcdef')
    print creds
    print decrypt_dict(creds, key='0123456789abcdef')
