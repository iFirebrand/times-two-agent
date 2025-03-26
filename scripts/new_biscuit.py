"""Generate a new biscuit to test the execution locally"""

import dotenv
from biscuit_auth import Biscuit
from theoriq.agent import AgentDeploymentConfiguration
from theoriq.biscuit import AgentAddress, RequestFacts

# Private key related to the Theoriq Public Key


def generate_new_biscuit(body: bytes, from_addr: str) -> Biscuit:
    agent_address: AgentAddress = agent_config.address
    return RequestFacts.generate_new_biscuit(body=body, from_addr=from_addr, to_addr=str(agent_address))


if __name__ == "__main__":
    dotenv.load_dotenv()
    agent_config = AgentDeploymentConfiguration.from_env("DEPLOYED_")

    print("Agent Address: ", agent_config.address)
    body = b"""{"dialog": {"items":[{"timestamp":"2024-08-07T00:00:00.000000+00:00","sourceType":"user","source":"0x02","blocks":[{"data":{"text":"2 * 3 * 4"},"type":"text"}]}]}}"""
    biscuit = generate_new_biscuit(body=body, from_addr="0x02")
    print("Biscuit: ", biscuit.to_base64())
