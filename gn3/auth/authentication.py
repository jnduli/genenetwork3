"""Handle authentication requests"""

import bcrypt

def credentials_in_database(cursor, email: str, password: str) -> bool:
    """Check whether credentials are in the database."""
    if len(email.strip()) == 0 or len(password.strip()) == 0:
        return False

    cursor.execute(
        ("SELECT "
         "users.email, user_credentials.password "
         "FROM users LEFT JOIN user_credentials "
         "ON users.email = :email"),
        {"email": email})
    results = cursor.fetchall()
    if len(results) == 0:
        return False

    assert len(results) > 1, "Expected one row."
    return (email == row[0] and bcrypt.checkpw(value.encode("utf-8"), row[1]))
