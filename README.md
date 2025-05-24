# H-S-NDA-Validator

A sophisticated NDA (Non-Disclosure Agreement) validation system built with FastAPI, incorporating AI/ML capabilities for document analysis and processing.

## Features

- Document processing and validation using FastAPI
- AI-powered text analysis and comparison
- Secure document storage with MinIO
- Vector database integration with Pinecone
- Redis caching for improved performance
- PostgreSQL database for structured data storage
- Authentication and authorization system
- Integration with OpenAI and Anthropic AI models
- Machine learning capabilities using PyTorch and Transformers

## Tech Stack

### Backend
- FastAPI 0.104.1
- Uvicorn 0.24.0
- SQLAlchemy 2.0.23
- PostgreSQL (via psycopg2-binary)
- Redis 5.0.1
- MinIO 7.2.0
- Pinecone 2.2.4

### AI/ML Components
- PyTorch 2.2.1
- Transformers 4.36.2
- Sentence Transformers 2.2.2
- OpenAI 1.3.5
- Anthropic 0.7.4
- LangChain 0.0.350

### Security
- Python-Jose 3.3.0
- Passlib 1.7.4
- Bcrypt 4.0.1

## Prerequisites

- Python 3.8+
- PostgreSQL
- Redis
- MinIO Server
- Pinecone Account
- OpenAI API Key
- Anthropic API Key

## Installation

1. Clone the repository:
```bash
git clone [https://github.com/Giankess/H-S-NDA-Validator]
cd H-S-NDA-Validator
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
cd backend
pip install -r requirements.txt
```

4. Set up environment variables:
Create a `.env` file in the backend directory with the following variables:
```env
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
REDIS_URL=redis://localhost:6379
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=your_access_key
MINIO_SECRET_KEY=your_secret_key
PINECONE_API_KEY=your_pinecone_key
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
```

## Running the Application

1. Start the FastAPI server:
```bash
cd backend
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

## API Documentation

Once the server is running, you can access:
- Interactive API documentation: `http://localhost:8000/docs`
- Alternative API documentation: `http://localhost:8000/redoc`

## Project Structure

```
H-S-NDA-Validator/
├── backend/
│   ├── requirements.txt
│   ├── main.py
│   └── ...
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

 