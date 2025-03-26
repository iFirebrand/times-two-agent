from biscuit_auth import Biscuit, PublicKey, BlockBuilder, KeyPair, PrivateKey
import httpx
from datetime import datetime, timezone
from pprint import pprint
import os
import dotenv
from theoriq.biscuit import get_new_key_pair

def cyan(text):
    # ANSI escape code for light grey text
    CYAN = "\033[0;36m"  # Light grey text
    RESET = "\033[0m"
    return f"{CYAN}{text}{RESET}"

def ask_user_input(prompt, default=None):
    """Ask for user input with a default value."""
    user_input = input(cyan(f"{prompt} [{default}]: ")).strip()
    return user_input if user_input else default

# Load environment variables
dotenv.load_dotenv()

# Fetch the public key from the API
base_api_url = "https://theoriq-backend.dev-02.lab.chainml.net/api/v1alpha2"
public_key_url = f"{base_api_url}/auth/biscuits/public-key"
response = httpx.get(public_key_url)
print("Public key response:", response.json())  # Print the full response to see its structure

# Get API key from environment variables
biscuit_raw = os.getenv("THEORIQ_API_KEY")
if not biscuit_raw:
    raise ValueError("THEORIQ_API_KEY environment variable is not set")

# Use a default public key for now (we'll update this after seeing the API response structure)
public_key_raw = "0x3363f11284bc2671356a847312dfe4e323f8e82e2032fe69e7e079ff3d1c86bf"
public_key = PublicKey.from_hex(public_key_raw.removeprefix("0x"))

token = Biscuit.from_base64(biscuit_raw, public_key)

# Set fixed expiry timestamp (December 31, 2025, 00:00:00 UTC)
expiry_timestamp = 1767139200
block_builder = BlockBuilder(f"theoriq:expires_at({expiry_timestamp})")

# Generate new key pair using the same method as generate_private_key.py
public_key, agent_private_key_raw = get_new_key_pair()
print(f"Generated private key: {agent_private_key_raw}")
print(f"Corresponding public key: {public_key}")

agent_private_key = PrivateKey.from_hex(agent_private_key_raw.removeprefix("0x"))
agent_kp = KeyPair.from_private_key(agent_private_key)

attenuated_biscuit = token.append_third_party_block(agent_kp, block_builder)

# Get the access token
access_token_url = f"{base_api_url}/auth/api-keys/exchange"
response = httpx.post(access_token_url, headers={"Authorization": f"Bearer {attenuated_biscuit.to_base64()}"})

pprint(response.json())




