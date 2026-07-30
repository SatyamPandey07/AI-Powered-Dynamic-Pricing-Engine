# Getting Started

## Prerequisites
- Docker and Docker Compose
- Node.js 20+
- Python 3.11+

## Local Development Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/SatyamPandey07/AI-Powered-Dynamic-Pricing-Engine.git
   cd AI-Powered-Dynamic-Pricing-Engine
   ```

2. **Start Infrastructure:**
   ```bash
   cd infra
   docker-compose up -d
   ```
   *This starts Postgres, Redis, Prometheus, Grafana, Loki, and Promtail.*

3. **Start Backend:**
   ```bash
   cd backend
   poetry install
   poetry run uvicorn app.main:app --reload
   ```

4. **Start Frontend:**
   ```bash
   cd frontend
   npm ci
   npm run dev
   ```

5. **Access the App:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000/docs
   - Grafana: http://localhost:3001
