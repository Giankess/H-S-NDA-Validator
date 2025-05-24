# H-S-NDA-Validator

A sophisticated NDA (Non-Disclosure Agreement) validation system built with FastAPI, incorporating AI/ML capabilities for document analysis and processing. The system is completely self-contained and runs entirely in Docker containers.

## Features

- Document processing and validation using FastAPI
- AI-powered text analysis and comparison using local models
- Secure document storage with MinIO
- Vector database integration with Qdrant
- Redis caching for improved performance
- PostgreSQL database for structured data storage
- Authentication and authorization system
- Local machine learning capabilities using PyTorch and Transformers

## Tech Stack

### Backend
- FastAPI 0.104.1
- Uvicorn 0.24.0
- SQLAlchemy 2.0.23
- PostgreSQL (via psycopg2-binary)
- Redis 5.0.1
- MinIO 7.2.0
- Qdrant 1.7.0

### AI/ML Components
- PyTorch 2.2.1
- Transformers 4.36.2
- Sentence Transformers 2.2.2
- LangChain 0.0.350

### Security
- Python-Jose 3.3.0
- Passlib 1.7.4
- Bcrypt 4.0.1

## Prerequisites

- Docker
- Docker Compose

## Installation

1. Clone the repository:
```bash
git clone [https://github.com/Giankess/H-S-NDA-Validator]
cd H-S-NDA-Validator
```

2. Start the application:
```bash
docker-compose up --build
```

The application will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- MinIO Console: http://localhost:9001
- API Documentation: http://localhost:8000/docs

## Project Structure

```
H-S-NDA-Validator/
├── backend/
│   ├── requirements.txt
│   ├── main.py
│   └── ...
├── frontend/
│   ├── package.json
│   └── ...
├── docker-compose.yml
└── README.md
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

## Contact

 