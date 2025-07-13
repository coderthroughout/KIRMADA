# Aztec Protocol Backend

A comprehensive backend API for the Aztec Protocol - a decentralized AI collaboration system using zero-knowledge proofs (ZKPs) and IPFS for privacy-preserving model training and verification.

## 🚀 Features

- **🔐 Authentication & Authorization**: JWT-based user authentication with role-based access control
- **🤖 AI Agent Management**: Complete lifecycle management for AI training agents
- **🧠 Model Management**: Upload, train, and manage AI models with IPFS storage
- **🔍 ZK Proof System**: Generate and verify zero-knowledge proofs for training verification
- **⛓️ Blockchain Integration**: Smart contract interaction for proof verification
- **🌐 IPFS Integration**: Decentralized file storage with Pinata integration
- **🔄 Collaboration Rounds**: Multi-agent training rounds and coordination
- **📊 Real-time Monitoring**: Health checks, metrics, and performance tracking
- **📝 Comprehensive Logging**: Detailed request/response logging
- **🧪 Testing Suite**: Complete API testing framework

## 📋 Prerequisites

- Python 3.8+
- PostgreSQL (recommended) or SQLite
- Redis (optional, for caching and task queue)
- Node.js (for blockchain integration)

## 🛠️ Quick Start

### 1. Clone and Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Environment Configuration

Copy the example environment file and configure it:

```bash
cp .env.example .env
# Edit .env with your configuration
```

### 3. Database Setup

**Option A: SQLite (Default)**
```bash
# No additional setup needed - SQLite will be created automatically
```

**Option B: PostgreSQL**
```bash
# Install PostgreSQL and create database
createdb aztec_backend
# Update DATABASE_URL in .env
```

### 4. Start the Backend

**Option A: Using the startup script (Recommended)**
```bash
python start_backend.py
```

**Option B: Direct uvicorn**
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 5. Verify Installation

```bash
# Test the API
curl http://localhost:8000/health
curl http://localhost:8000/info

# Run comprehensive tests
python test_backend.py
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DEBUG` | Enable debug mode | `true` |
| `HOST` | Server host | `0.0.0.0` |
| `PORT` | Server port | `8000` |
| `SECRET_KEY` | JWT secret key | Auto-generated |
| `DATABASE_URL` | Database connection | `sqlite:///./aztec.db` |
| `REDIS_URL` | Redis connection | `redis://localhost:6379` |
| `ETHEREUM_RPC_URL` | Ethereum RPC | `http://localhost:8545` |
| `IPFS_API_KEY` | Pinata API key | From agent config |
| `IPFS_API_SECRET` | Pinata API secret | From agent config |

### IPFS Configuration

The backend automatically uses the Pinata credentials from your agent configuration:

```toml
# From aztec-agent.toml
pinata_api_key = "f4545a3af6185deca569"
pinata_secret_key = "10248cde2fff76a5ca689a30708c07b7a4e2ac62bd3c18ff9f67029d74e85ef7"
```

## 📚 API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health
- **API Info**: http://localhost:8000/info

## 🔌 API Endpoints

### Authentication
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/token` - Login
- `GET /api/v1/auth/me` - Get current user
- `POST /api/v1/auth/refresh` - Refresh token

### Agents
- `GET /api/v1/agents` - List agents
- `POST /api/v1/agents` - Create agent
- `GET /api/v1/agents/{id}` - Get agent
- `PUT /api/v1/agents/{id}` - Update agent
- `DELETE /api/v1/agents/{id}` - Delete agent
- `POST /api/v1/agents/{id}/start` - Start agent training
- `POST /api/v1/agents/{id}/stop` - Stop agent training
- `GET /api/v1/agents/{id}/status` - Get agent status
- `POST /api/v1/agents/{id}/config` - Update agent config
- `POST /api/v1/agents/{id}/upload-config` - Upload config file
- `GET /api/v1/agents/{id}/logs` - Get agent logs

### Models
- `GET /api/v1/models` - List models
- `POST /api/v1/models` - Create model
- `GET /api/v1/models/{id}` - Get model
- `PUT /api/v1/models/{id}` - Update model
- `DELETE /api/v1/models/{id}` - Delete model
- `POST /api/v1/models/upload` - Upload model file
- `POST /api/v1/models/{id}/upload-to-ipfs` - Upload to IPFS
- `GET /api/v1/models/{id}/download` - Get download info
- `GET /api/v1/models/{id}/training-stats` - Get training stats
- `POST /api/v1/models/{id}/evaluate` - Evaluate model

### Proofs
- `GET /api/v1/proofs` - List proofs
- `POST /api/v1/proofs` - Create proof
- `GET /api/v1/proofs/{id}` - Get proof
- `PUT /api/v1/proofs/{id}` - Update proof
- `DELETE /api/v1/proofs/{id}` - Delete proof
- `POST /api/v1/proofs/generate` - Generate proof from training data
- `POST /api/v1/proofs/{id}/verify` - Verify proof
- `POST /api/v1/proofs/{id}/upload` - Upload proof to IPFS
- `POST /api/v1/proofs/{id}/submit-to-blockchain` - Submit to blockchain
- `GET /api/v1/proofs/{id}/download` - Get proof download info
- `POST /api/v1/proofs/upload-proof-file` - Upload proof file

### IPFS
- `POST /api/v1/ipfs/upload` - Upload file to IPFS
- `GET /api/v1/ipfs/{hash}` - Get file from IPFS
- `DELETE /api/v1/ipfs/{hash}` - Delete file from IPFS
- `POST /api/v1/ipfs/upload-multiple` - Upload multiple files
- `GET /api/v1/ipfs/status` - Get IPFS service status
- `POST /api/v1/ipfs/upload-directory` - Upload directory structure
- `GET /api/v1/ipfs/gateways` - Get available gateways

### Blockchain
- `GET /api/v1/blockchain/status` - Blockchain status
- `GET /api/v1/blockchain/contracts` - Get contract addresses
- `POST /api/v1/blockchain/submit-proof` - Submit proof to blockchain
- `POST /api/v1/blockchain/verify-proof` - Verify proof on blockchain
- `GET /api/v1/blockchain/transactions` - Get transaction history
- `GET /api/v1/blockchain/events` - Get contract events
- `POST /api/v1/blockchain/deploy-contracts` - Deploy contracts
- `GET /api/v1/blockchain/gas-estimate` - Estimate gas costs

## 🧪 Testing

### Run All Tests
```bash
python test_backend.py
```

### Manual Testing with curl

```bash
# Health check
curl http://localhost:8000/health

# Register user
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@aztec.com","password":"testpass","full_name":"Test User","wallet_address":"0x123..."}'

# Login
curl -X POST http://localhost:8000/api/v1/auth/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test@aztec.com&password=testpass"

# Create agent (with token)
curl -X POST http://localhost:8000/api/v1/agents \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"name":"test-agent","agent_type":"training",...}'
```

## 📊 Database Models

### User
- Authentication and user management
- Wallet address association
- Role-based permissions

### Agent
- AI agent lifecycle management
- Configuration storage
- Performance metrics
- Training status tracking

### Model
- AI model metadata
- IPFS hash storage
- Training statistics
- Evaluation results

### Proof
- ZK proof storage
- Verification results
- Blockchain transaction hashes
- Training data association

### Round
- Collaboration round management
- Agent participation tracking
- Round status and results

## 🔐 Security Features

- **JWT Authentication**: Secure token-based authentication
- **Password Hashing**: Bcrypt password hashing
- **CORS Protection**: Configurable CORS policies
- **Input Validation**: Comprehensive request validation
- **Error Handling**: Secure error responses
- **Rate Limiting**: Configurable rate limiting
- **Logging**: Comprehensive security logging

## 🌐 IPFS Integration

The backend integrates with Pinata IPFS service:

- **File Upload**: Upload models, proofs, and metadata
- **File Retrieval**: Get files from IPFS gateways
- **File Management**: Pin/unpin files
- **Batch Operations**: Upload multiple files
- **Verification**: Verify file accessibility
- **Compression**: Automatic compression for large files

## ⛓️ Blockchain Integration

Smart contract interaction features:

- **Proof Submission**: Submit proofs to blockchain
- **Proof Verification**: Verify proofs on-chain
- **Contract Events**: Monitor contract events
- **Gas Estimation**: Estimate transaction costs
- **Transaction History**: Track blockchain transactions
- **Contract Deployment**: Deploy smart contracts

## 🔍 ZK Proof System

Zero-knowledge proof capabilities:

- **Proof Generation**: Generate ZK proofs from training data
- **Proof Verification**: Verify proofs cryptographically
- **Training Verification**: Verify training process integrity
- **Data Integrity**: Ensure data hasn't been tampered with
- **Model Diff Proofs**: Verify model parameter changes

## 📈 Monitoring & Logging

- **Health Checks**: Comprehensive health monitoring
- **Performance Metrics**: Request/response timing
- **Error Tracking**: Detailed error logging
- **Resource Monitoring**: CPU, memory, disk usage
- **API Metrics**: Endpoint usage statistics

## 🚀 Deployment

### Development
```bash
python start_backend.py
```

### Production
```bash
# Using gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# Using Docker
docker build -t aztec-backend .
docker run -p 8000:8000 aztec-backend
```

### Environment Variables for Production
```bash
DEBUG=false
SECRET_KEY=your-production-secret-key
DATABASE_URL=postgresql://user:pass@host:port/db
REDIS_URL=redis://host:port
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- **Documentation**: Check the `/docs` endpoint for API documentation
- **Issues**: Report bugs and feature requests via GitHub issues
- **Discussions**: Join community discussions for questions and ideas

## 🔗 Related Projects

- **Agent**: AI training agent implementation
- **Contracts**: Smart contract implementation
- **Circuits**: ZK proof circuits
- **Frontend**: Web interface (coming soon)

---

**Built with ❤️ for the decentralized AI future** 