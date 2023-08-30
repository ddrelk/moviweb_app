import uuid
import bcrypt


def id_generator():
    """Generates a unique ID using UUID."""
    return str(uuid.uuid4())


def generate_password_hash(plain_password):
    hashed_password = bcrypt.hashpw(plain_password.encode('utf-8'), bcrypt.gensalt())
    return hashed_password.decode('utf-8')


def check_password_hash(hashed_password, plain_password):
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
