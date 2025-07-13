# Aztec Protocol Backend Setup Guide

## 🗄️ PostgreSQL Setup

### 1. Install PostgreSQL

**Windows:**
```bash
# Download from https://www.postgresql.org/download/windows/
# Or use Chocolatey:
choco install postgresql
```

**macOS:**
```bash
brew install postgresql
brew services start postgresql
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

### 2. Create Database and User

```bash
# Connect to PostgreSQL as superuser
sudo -u postgres psql

# Create database (using default postgres user)
CREATE DATABASE aztec_db;
\q
```

### 3. Update Environment Configuration

Create `.env` file:
```bash
cp .env.example .env
```

Edit `.env` with your PostgreSQL credentials:
```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/aztec_db
```

## 🚀 Backend Setup

### 1. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 2. Start the Backend
```bash
python start.py
```

The server will start at: http://localhost:8000

## 🧪 API Testing Guide

### 1. **Swagger UI (Interactive Documentation)**
Visit: http://localhost:8000/docs

This provides:
- ✅ Interactive API documentation
- ✅ Try out endpoints directly
- ✅ Request/response examples
- ✅ Authentication testing

### 2. **Health Check**
```bash
curl http://localhost:8000/health
```
Expected response:
```json
{
  "status": "healthy",
  "service": "aztec-protocol-backend",
  "version": "1.0.0"
}
```

### 3. **Authentication Endpoints**

#### Register a User
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "testpassword123",
    "full_name": "Test User"
  }'
```

#### Login
```bash
curl -X POST "http://localhost:8000/api/v1/auth/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser&password=testpassword123"
```

#### Get Current User (with token)
```bash
curl -X GET "http://localhost:8000/api/v1/auth/me" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### 4. **Agent Endpoints**

#### List Agents
```bash
curl -X GET "http://localhost:8000/api/v1/agents" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

#### Create Agent
```bash
curl -X POST "http://localhost:8000/api/v1/agents" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My AI Agent",
    "description": "A test agent",
    "agent_type": "training"
  }'
```

### 5. **Model Endpoints**

#### List Models
```bash
curl -X GET "http://localhost:8000/api/v1/models" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

#### Upload Model
```bash
curl -X POST "http://localhost:8000/api/v1/models" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -F "file=@your_model_file.json" \
  -F "name=My Model" \
  -F "model_type=transformer"
```

### 6. **Proof Endpoints**

#### List Proofs
```bash
curl -X GET "http://localhost:8000/api/v1/proofs" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

#### Generate Proof
```bash
curl -X POST "http://localhost:8000/api/v1/proofs" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "proof_type": "training_proof",
    "model_id": 1,
    "circuit_name": "training_proof"
  }'
```

### 7. **Round Endpoints**

#### List Rounds
```bash
curl -X GET "http://localhost:8000/api/v1/rounds" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

#### Create Round
```bash
curl -X POST "http://localhost:8000/api/v1/rounds" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Collaboration Round 1",
    "description": "First AI collaboration round",
    "bounty_amount": 100.0
  }'
```

## 🔧 Testing with Python

### 1. **Using requests library**
```python
import requests

# Base URL
BASE_URL = "http://localhost:8000"

# Register user
response = requests.post(f"{BASE_URL}/api/v1/auth/register", json={
    "username": "testuser",
    "email": "test@example.com", 
    "password": "testpassword123",
    "full_name": "Test User"
})
print("Register:", response.json())

# Login
response = requests.post(f"{BASE_URL}/api/v1/auth/token", data={
    "username": "testuser",
    "password": "testpassword123"
})
token = response.json()["access_token"]

# Get current user
headers = {"Authorization": f"Bearer {token}"}
response = requests.get(f"{BASE_URL}/api/v1/auth/me", headers=headers)
print("Current user:", response.json())
```

### 2. **Using curl with token variable**
```bash
# Store token in variable
TOKEN=$(curl -s -X POST "http://localhost:8000/api/v1/auth/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser&password=testpassword123" | jq -r '.access_token')

# Use token in requests
curl -X GET "http://localhost:8000/api/v1/agents" \
  -H "Authorization: Bearer $TOKEN"
```

## 📊 Database Verification

### Check Database Tables
```bash
# Connect to PostgreSQL
psql -U postgres -d aztec_db -h localhost

# List tables
\dt

# Check users table
SELECT * FROM users;

# Check agents table  
SELECT * FROM agents;

# Exit
\q
```

## 🐛 Troubleshooting

### Common Issues:

1. **PostgreSQL Connection Error**
   - Check if PostgreSQL is running
   - Verify credentials in `.env`
   - Ensure database exists

2. **Import Errors**
   - Install missing dependencies: `pip install -r requirements.txt`
   - Check Python version (3.8+)

3. **Port Already in Use**
   - Change port in `.env`: `PORT=8001`
   - Or kill existing process

4. **Authentication Errors**
   - Check token format: `Bearer YOUR_TOKEN`
   - Verify token hasn't expired
   - Re-login to get new token

## 🎯 Quick Test Script

Create `test_api.py`:
```python
import requests
import json

BASE_URL = "http://localhost:8000"

def test_api():
    # Health check
    response = requests.get(f"{BASE_URL}/health")
    print("Health:", response.json())
    
    # Register user
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpassword123",
        "full_name": "Test User"
    }
    response = requests.post(f"{BASE_URL}/api/v1/auth/register", json=user_data)
    print("Register:", response.json())
    
    # Login
    login_data = {
        "username": "testuser",
        "password": "testpassword123"
    }
    response = requests.post(f"{BASE_URL}/api/v1/auth/token", data=login_data)
    token = response.json()["access_token"]
    print("Login successful, token received")
    
    # Test authenticated endpoint
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/v1/agents", headers=headers)
    print("Agents:", response.json())

if __name__ == "__main__":
    test_api()
```

Run: `python test_api.py`

---

**🎉 Your backend is now ready for frontend integration!** 