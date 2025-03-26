import os
from pathlib import Path

import dotenv
import httpx
import yaml
from biscuit_auth import Biscuit, PublicKey, BlockBuilder, KeyPair, PrivateKey
from theoriq.agent import AgentDeploymentConfiguration
from theoriq.biscuit import get_new_key_pair

# Load environment variables
dotenv.load_dotenv()

def create_agent_yaml():
    """Create the agent YAML configuration file."""
    agent_config = {
        "name": "awesome-multiplication-agent",
        "description": "An agent that performs multiplication operations",
        "version": "1.0.0",
        "schema": {
            "type": "object",
            "properties": {
                "prefix": {"type": "string"},
                "offset": {"type": "integer"}
            }
        }
    }
    
    # Create data directory if it doesn't exist
    data_dir = Path("../data")
    data_dir.mkdir(exist_ok=True)
    
    # Write the YAML file
    yaml_path = data_dir / "agent.yaml"
    with open(yaml_path, "w") as f:
        yaml.dump(agent_config, f)
    
    return str(yaml_path.absolute())

def get_access_token():
    """Exchange API key for an access token."""
    api_key = os.getenv("THEORIQ_API_KEY")
    if not api_key:
        raise ValueError("THEORIQ_API_KEY environment variable is not set")

    # Fetch the public key from the API
    base_api_url = os.environ["THEORIQ_URI"]
    public_key_url = f"{base_api_url}/api/v1alpha2/auth/biscuits/public-key"
    response = httpx.get(public_key_url)
    public_key_raw = response.json()["publicKey"]
    public_key = PublicKey.from_hex(public_key_raw.removeprefix("0x"))

    # Parse the existing token with the public key
    token = Biscuit.from_base64(api_key, public_key)

    # Set fixed expiry timestamp (December 31, 2025, 00:00:00 UTC)
    expiry_timestamp = 1767139200
    block_builder = BlockBuilder(f"theoriq:expires_at({expiry_timestamp})")

    # Generate new key pair
    public_key, agent_private_key_raw = get_new_key_pair()
    print(f"Generated private key: {agent_private_key_raw}")
    print(f"Corresponding public key: {public_key}")

    # Save the generated private key to .env file for future use
    with open(".env", "a") as f:
        f.write(f"\nAGENT_PRIVATE_KEY = {agent_private_key_raw}\n")

    agent_private_key = PrivateKey.from_hex(agent_private_key_raw.removeprefix("0x"))
    agent_kp = KeyPair.from_private_key(agent_private_key)

    # Create attenuated token with expiration
    attenuated_biscuit = token.append_third_party_block(agent_kp, block_builder)

    # Exchange the attenuated token for an access token
    access_token_url = f"{base_api_url}/api/v1alpha2/auth/api-keys/exchange"
    response = httpx.post(
        access_token_url,
        headers={
            "Authorization": f"Bearer {attenuated_biscuit.to_base64()}",
            "Content-Type": "application/json"
        }
    )

    try:
        response.raise_for_status()
    except httpx.HTTPStatusError as e:
        print(f"Error status code: {e.response.status_code}")
        print(f"Error response headers: {e.response.headers}")
        print(f"Error response body: {e.response.text}")
        raise

    result = response.json()
    print("Token exchange response:", result)
    return result["biscuit"]

def deploy_agent():
    """Deploy the agent to Theoriq."""
    # Create agent YAML if it doesn't exist
    yaml_path = create_agent_yaml()
    
    try:
        # Get the agent configuration
        agent_config = AgentDeploymentConfiguration.from_env("DEPLOYED_")
        
        # Read the YAML file
        with open(yaml_path) as f:
            agent_yaml = yaml.safe_load(f)
        
        # Get the deployment URL from environment variable
        deployment_url = os.environ.get("AGENT_DEPLOYMENT_URL")
        if not deployment_url:
            raise ValueError("AGENT_DEPLOYMENT_URL environment variable is not set. Please set it to your public agent URL (e.g., from ngrok).")
        
        # Generate the request body exactly as shown in the documentation
        request_body = {
            "metadata": {
                "name": "Awesome Multiplication Agent",
                "shortDescription": "An agent that performs multiplication operations",
                "longDescription": "This agent takes numbers as input and multiplies them together. It can handle multiple numbers in a single request and supports configuration for prefix and offset.",
                "tags": ["Math", "Multiplication", "Calculator"],
                "costCard": "Cost is based on the result of the multiplication",
                "examplePrompts": [
                    "2 * 3",
                    "4 * 5 * 6"
                ]
            },
            "configuration": {
                "deployment": {
                    "url": deployment_url,
                    "headers": []  # Empty array instead of array with null values
                }
            }
        }
        
        # Get access token with expiration
        access_token = get_access_token()
        
        # Prepare the deployment request
        deploy_url = f"{os.environ['THEORIQ_URI']}/api/v1alpha2/agents"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}"
        }
        
        # Deploy the agent
        with httpx.Client() as client:
            response = client.post(
                deploy_url,
                json=request_body,
                headers=headers
            )
            
            if response.status_code == 201:
                result = response.json()
                print(f"Agent deployed successfully!")
                print(f"Agent Address: {result.get('agent_address', 'N/A')}")
                print(f"Transaction Hash: {result.get('transaction_hash', 'N/A')}")
                return result
            else:
                print(f"Failed to deploy agent: {response.status_code}")
                print(f"Response: {response.text}")
                response.raise_for_status()
                
    except Exception as e:
        print(f"Failed to deploy agent: {str(e)}")
        raise

if __name__ == "__main__":
    deploy_agent() 