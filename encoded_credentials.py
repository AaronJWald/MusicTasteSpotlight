import base64

def get_credentials():
    # Replace these values with your actual credentials
    #These are obtained through spotify for developers and creating an app
    #This, of course, isn't really secure, but it does prevent having my credentials on my screen at any point.
    username = "client_id_here"
    password = "client_secret_here"

    # Obfuscate the credentials using base64 encoding
    obfuscated_username = base64.b64encode(username.encode()).decode()
    obfuscated_password = base64.b64encode(password.encode()).decode()

    return obfuscated_username, obfuscated_password
