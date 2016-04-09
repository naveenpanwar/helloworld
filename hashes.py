import hashlib
import hmac
import random
import string

SECRET = "TORSO"
#########################################################################################
#                           hashing functions
#########################################################################################
class Hashers():
    def hash_digest(self, string, algo):
        return hmac.new(SECRET, string, algo).hexdigest()

    def hash_str(self, string, algo):
        return "%s|%s"%( string, self.hash_digest(string, algo) )

    def check_hash_str(self, string, algo):
        value = string.split('|')[0]
        if string == self.hash_str(value, algo):
            return value
    
    @classmethod
    def make_salt(cls):
        return "".join(random.choice(string.letters) for x in xrange(10))
    
    @classmethod
    def make_pw_hash(cls, name, pw, salt=None):
        if not salt:
            salt = cls.make_salt()
        return "%s|%s" % (salt, hashlib.sha256(name+pw+salt).hexdigest())
    
    @classmethod
    def check_pw_hash(cls, name, pw, pw_hash):
        salt = pw_hash.split('|')[0]
        return pw_hash == cls.make_pw_hash(name, pw, salt)

