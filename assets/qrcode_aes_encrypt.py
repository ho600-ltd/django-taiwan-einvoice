from base64 import b64encode, b64decode
from Crypto.Cipher import AES
from binascii import unhexlify 


def _pad(byte_array):
    BLOCK_SIZE = 16
    pad_len = BLOCK_SIZE - len(byte_array) % BLOCK_SIZE
    return byte_array + (bytes([pad_len]) * pad_len)


def _unpad(byte_array):
    last_byte = byte_array[-1]
    return byte_array[0:-last_byte]

def qrcode_aes_encrypt(key, plain_text):
    iv = b64decode('Dt8lyToo17X/XkXaQvihuA==')
    key = unhexlify(key)
    cipher = AES.new(key, mode=AES.MODE_CBC, IV=iv)
    pad_string = _pad(plain_text.encode('utf-8'))
    return b64encode(cipher.encrypt(pad_string)).decode('utf-8')


if '__main__' == __name__:
    import sys
    result = qrcode_aes_encrypt(*sys.argv[1:])
    print(result)