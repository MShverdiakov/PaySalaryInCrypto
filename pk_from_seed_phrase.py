from mnemonic import Mnemonic
import bip32utils
import hashlib
import binascii

# Define your mnemonic phrase (12, 18, or 24 words)
mnemonic_phrase = (''
                   '')

# Create a Mnemonic object for the English language
mnemo = Mnemonic("english")

# Generate the seed from the mnemonic phrase
seed = mnemo.to_seed(mnemonic_phrase)

# Derive the private key using the BIP-44 path m/44'/195'/0'/0/0 for TRON
bip32_root_key_obj = bip32utils.BIP32Key.fromEntropy(seed)
bip32_child_key_obj = bip32_root_key_obj.ChildKey(44 + bip32utils.BIP32_HARDEN) \
                                         .ChildKey(195 + bip32utils.BIP32_HARDEN) \
                                         .ChildKey(0 + bip32utils.BIP32_HARDEN) \
                                         .ChildKey(0) \
                                         .ChildKey(0)

private_key_hex = bip32_child_key_obj.PrivateKey().hex()
print(f"Private Key: {private_key_hex}")