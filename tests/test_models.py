from werkzeug.security import generate_password_hash, check_password_hash


def test_user_password_hashing_behaves_correctly():
    password = "meinPasswort123"
    password_hash = generate_password_hash(password)

    #hash soll nicht das gleiche wie das Passwort sein
    assert password_hash != password

    #sollte True zurückgeben bei richtigem Passwort
    assert check_password_hash(password_hash, password) is True

    #sollte False zurückgeben bei falschem Passwort
    assert check_password_hash(password_hash, "falschesPasswort") is False