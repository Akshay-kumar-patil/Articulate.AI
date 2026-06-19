import bcrypt

def hash_password(password: str) -> str:

    # Convert string to bytes because bcrypt works with bytes
    password_bytes = password.encode("utf-8")

    # Generate a salted hash
    hashed_password = bcrypt.hashpw(password_bytes, bcrypt.gensalt())

    # Convert bytes back to string for MongoDB storage
    return hashed_password.decode("utf-8")


def verify_password(password: str, hashed_password: str) -> bool:

    return bcrypt.checkpw(
        password.encode("utf-8"),
        hashed_password.encode("utf-8")
    )