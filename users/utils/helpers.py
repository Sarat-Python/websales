import random
import hashlib

def activation_code(email):
    salt = hashlib.sha1(str(random.random())).hexdigest()[:5]
    code = hashlib.sha1(salt+email).hexdigest()[:6]
    return code
