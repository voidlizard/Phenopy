import random, md5

characters = 'qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM1234567890-'

def generate(password=None, length=8, salt_length=10):
    global characters
    passwd = password
    if not password:
        passwd = ''.join(random.sample(characters, length))
    passwd_salt = ''.join(random.sample(characters, salt_length))
    passwd_hash = md5.md5(passwd+passwd_salt).hexdigest()
    return (passwd, passwd_hash, passwd_salt)
    

def check(passwd, hash, salt):
    return md5.md5(passwd+salt).hexdigest() == hash

