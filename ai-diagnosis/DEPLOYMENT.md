# 🚀 AI Diagnosis API Deployment Guide

## Quick Start

### 1. Check PostgreSQL Status

```bash
# Check if PostgreSQL is running locally
cd api && uv run python ../scripts/check_postgres.py

# Or manually check
psql -h localhost -p 5432 -U postgres -c "SELECT version();"
```

### 2. Deploy with Docker (Recommended)

```bash
# 1. Copy environment config
cp config.example .env

# 2. Update .env with your API keys and passwords

# 3. Deploy everything
./scripts/deploy.sh
```

### 3. Manual Setup

```bash
# Install dependencies (using uv - much faster than pip)
cd api
uv sync

# Set environment variables
export DATABASE_URL="postgresql://user:password@host:port/database"
export OPENAI_API_KEY="your_openai_key"

# Run the API
uv run uvicorn main:app --reload
```

> 💡 **Why uv?** This project uses [uv](https://docs.astral.sh/uv/) instead of pip because it's:
> - **10-100x faster** dependency resolution and installation
> - **More reliable** with better conflict resolution  
> - **Modern Python toolchain** (project management, virtual envs, etc.)
> - **Drop-in replacement** for pip with better UX

## Deployment Options

### 🐳 Local Docker Deployment

```bash
# Start services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f api

# Stop services  
docker-compose down
```

### Health Check
```bash
curl http://localhost:8000/health
```

### Database Setup
```bash
# Create table
curl -X POST http://localhost:8000/sensors/admin/create-table

# Populate data
curl -X POST http://localhost:8000/sensors/admin/populate-database

# Complete setup
curl -X POST http://localhost:8000/sensors/admin/setup-database
```

### Data Access
```bash
# Get all sensor data
curl http://localhost:8000/sensors/all

# Get data by sensor ID
curl http://localhost:8000/sensors/by-sensor/GPD9132

# Get paginated data
curl "http://localhost:8000/sensors/data?skip=0&limit=10"
```

## URLs

- **API**: http://localhost:8000
- **Docs**: http://localhost:8000/docs
- **Health**: http://localhost:8000/health
- **PostgreSQL**: localhost:5432

## Troubleshooting

### PostgreSQL Connection Issues
```bash
# Check if PostgreSQL is running
sudo systemctl status postgresql

# Check port availability
netstat -an | grep 5432

# Test connection
cd api && uv run python ../scripts/check_postgres.py
```

### Docker Issues
```bash
# Rebuild containers
docker-compose down
docker-compose up --build -d

# View logs
docker-compose logs -f

# Reset volumes
docker-compose down -v
docker-compose up -d
```

### Environment Variables
```bash
# Check if variables are set
echo $DATABASE_URL
echo $OPENAI_API_KEY

# Load from .env file
source .env
```

## Production Deployment

For production, consider:
- Use managed PostgreSQL (Supabase, Railway, AWS RDS)
- Set up SSL certificates
- Configure reverse proxy (nginx)
- Use Docker containers with proper health checks
- Set up monitoring and logging
- Use secrets management for API keys
