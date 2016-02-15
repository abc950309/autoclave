from passlib.hash import sha256_crypt

def encrypt_password(password):
    return sha256_crypt.encrypt(password, rounds = 1000)

def verify_password(input_password, hashed):
    return sha256_crypt.verify(input_password, hashed)