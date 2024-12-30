# API Gateway Service

[System Overview Documentation](https://daffodil-throne-f06.notion.site/SamurAI-System-Overview-14c82c979e8480348029ec1cc43e9249?pvs=4)

Central gateway service managing authentication and routing for the SamurAI platform.

## System Overview
![System Architecture](https://github.com/itsomar278/samurai_video_service/blob/main/ezgif-4-77c29e34de%20(1).gif)

## Features
- JWT-based authentication
- Request routing to microservices
- RabbitMQ integration for video processing
- Unified API interface

## Prerequisites
- Python 3.8+
- RabbitMQ running on port 5672
- Flask

## Installation

1. Clone repository:
```bash
git clone https://github.com/itsomar278/samurai_api_gateway
cd samurai_api_gateway
```

2. Set up virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Start the service:
```bash
python app.py
```

## API Endpoints

### Authentication
- `POST /signup` - User registration
  ```json
  {
    "email": "string",
    "password": "string",
    "first_name": "string",
    "last_name": "string"
  }
  ```

- `POST /login` - User login
  ```json
  {
    "email": "string",
    "password": "string"
  }
  ```

### Video Processing
- `POST /process` - Submit video for processing
  ```json
  {
    "video_url": "string",
    "start_minute": "integer",
    "end_minute": "integer"
  }
  ```

- `GET /translation_status` - Check processing status
  ```
  ?request_id=string&user_id=string
  ```

- `GET /translations_by_user` - Get user's translations

### Content Interaction
- `POST /generate-quiz`
  ```json
  {
    "selected_index": "string",
    "user_id": "string",
    "total_questions": "integer",
    "hard_questions": "integer"
  }
  ```

- `POST /chat-with-content`
  ```json
  {
    "selected_index": "string",
    "user_id": "string",
    "user_query": "string",
    "chat_history": "string"
  }
  ```

- `POST /generate-summary`
  ```json
  {
    "selected_index": "string",
    "user_id": "string",
    "summary_length": "integer"
  }
  ```

- `POST /convert-to-article`
  ```json
  {
    "selected_index": "string",
    "user_id": "string"
  }
  ```

## Service Architecture
- Flask-based REST API
- JWT authentication middleware
- RabbitMQ client for async processing
- Service discovery and routing
- Error handling and validation

## Related Services
- [samurai_transclation_service](https://github.com/itsomar278/samurai_video_service)
- [samurai_auth_service](https://github.com/itsomar278/samurai_auth_service)
- [samurai_LLM_interaction_service](https://github.com/itsomar278/samurai_LLM_interaction)

