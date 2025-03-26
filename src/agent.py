import os
import subprocess
from flask import Flask, request, jsonify
import time
import json

app = Flask(__name__)

@app.route('/deployed', methods=['POST'])
def handle_request():
    data = request.get_json()
    # Your agent logic here
    return jsonify({"result": "success"})

@app.route('/deployed/public-key', methods=['GET'])
def get_public_key():
    # Read the agent's public key from .env file
    with open('.env', 'r') as f:
        for line in f:
            if line.startswith('AGENT_PRIVATE_KEY='):
                private_key = line.strip().split('=')[1]
                # Convert private key to public key (this is just a placeholder)
                # In reality, you should use proper key derivation
                public_key = "0x" + "0" * 64
                return jsonify({"publicKey": public_key})
    
    return jsonify({"error": "Public key not found"}), 404

if __name__ == '__main__':
    # Start localtunnel in the background
    port = int(os.environ.get('PORT', 8888))
    lt_process = subprocess.Popen(['lt', '--port', str(port)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # Wait for localtunnel to start and get the URL
    time.sleep(2)  # Give it a moment to start
    output = lt_process.stdout.readline().decode().strip()
    public_url = output.split('your url is: ')[1]
    
    print("\n" + "="*80)
    print(f"Agent URL: {public_url}/deployed")
    print("="*80 + "\n")
    
    # Save URL to .env file
    with open('.env', 'a') as f:
        f.write(f"\nAGENT_DEPLOYMENT_URL={public_url}/deployed\n")
    
    print("URL has been saved to .env file. Please run the following command in a new terminal:")
    print(f"export AGENT_DEPLOYMENT_URL={public_url}/deployed")
    
    # Start Flask app
    app.run(port=port, host='0.0.0.0') 