# Times Two Agent

A simple agent that takes a single number as input and returns its value multiplied by 2.

## 🚀 Features

- Simple number multiplication by 2
- Docker containerization
- Secure deployment configuration
- Cloud-ready setup
- Virtual environment management

## 🛠️ Prerequisites

- Python 3.10+
- Docker
- Git
- SSH access (for private package installation)

## 🏗️ Installation

1. Clone the repository:

```bash
git clone https://github.com/iFirebrand/awesome-multi-agent.git
cd awesome-multi-agent
```

2. Build the Docker image:

```bash
docker build -t awesome-multi-agent .
```

## 🚀 Running the Application

Run the container:

```bash
docker run -p 8080:8080 awesome-multi-agent
```

## 🏗️ Development

1. Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

## 🔒 Security Features

- Non-root user execution in Docker
- Secure file permissions
- SSH key management for private packages
- Virtual environment isolation

## 📝 License

MIT License

## 👥 Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request
