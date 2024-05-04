import os

aes_key = os.urandom(8)

# Convert the bytes to a hexadecimal string for easy representation
aes_key_hex = aes_key.hex()

print("Generated AES Key (hexadecimal):", aes_key_hex)
