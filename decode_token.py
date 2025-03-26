import os
import base64
from biscuit_auth import Biscuit
import dotenv

dotenv.load_dotenv()

def decode_token():
    api_key = os.getenv("THEORIQ_API_KEY")
    if not api_key:
        raise ValueError("THEORIQ_API_KEY environment variable is not set")
    
    try:
        # Remove any whitespace and newlines
        api_key = api_key.strip()
        
        # Decode base64
        decoded = base64.b64decode(api_key)
        print("Decoded token contents:")
        print(decoded)
        
        # Try to parse as Biscuit
        biscuit = Biscuit.from_base64(api_key)
        print("\nBiscuit token contents:")
        print(biscuit.print())
        
    except Exception as e:
        print(f"Error decoding token: {str(e)}")

if __name__ == "__main__":
    decode_token() 