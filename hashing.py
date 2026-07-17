import bcrypt

#hash using bcrypt
def hash_password(pword):
    byte_pword = pword.encode('utf-8')
    salt = bcrypt.gensalt()
    hash= bcrypt.hashpw(byte_pword, salt)
    return hash.decode('utf-8')

#validating hash as psw
def validate_hash(pword, stored_hash):
    hsh = stored_hash.encode('utf-8')
    byte_pword = pword.encode('utf-8')
    validate_hash = bcrypt.checkpw(byte_pword, hsh)
    return validate_hash