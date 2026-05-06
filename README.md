# CloudCart AI

A secure, AI-powered customer support system for the CloudCart e-commerce platform. Built with FastAPI backend, React frontend, and LangChain-powered agents using Google Gemini.

## Features

- **Secure AI Agent**: Hardened customer support assistant with input/output validation and security guardrails
- **Prompt Management**: Versioned prompt templates with persona configuration and few-shot examples
- **Model Fallbacks**: Automatic fallback to alternative Gemini models on failure
- **FastAPI Backend**: RESTful API with CORS support for seamless integration
- **React Frontend**: Modern web interface built with Vite and React
- **Comprehensive Validation**: Input sanitization and output filtering for safety
- **Environment Configuration**: Flexible settings management via environment variables

## Installation

### Prerequisites

- Python 3.8+
- Node.js 16+
- Google Gemini API key

### Backend Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd cloudcart_ai
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env and add your GOOGLE_API_KEY
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install Node.js dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```

## Usage

### Running the Backend

Start the FastAPI server:
```bash
python server.py
```

The API will be available at `http://localhost:8000`

### Running the Frontend

From the `frontend` directory:
```bash
npm run dev
```

The frontend will be available at `http://localhost:5173`

### Testing the Agent

Run the main script for a quick test:
```bash
python main.py
```

This will start an interactive chat session with the AI agent.

## API Endpoints

- `GET /api/health` - Health check endpoint
- `POST /api/chat` - Send a message to the AI agent

### Chat Endpoint Example

```bash
curl -X POST "http://localhost:8000/api/chat" \
     -H "Content-Type: application/json" \
     -d '{"message": "Where is my order?"}'
```

## Project Structure

```
cloudcart_ai/
├── main.py                 # Entry point with CLI chat interface
├── server.py               # FastAPI server
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
├── app/
│   ├── agents/
│   │   └── cloudcart_agent.py    # Main AI agent logic
│   ├── config/
│   │   └── settings.py           # Configuration management
│   ├── managers/
│   │   └── prompt_manager.py     # Prompt loading and management
│   ├── prompts/
│   │   ├── builder.py            # Prompt building utilities
│   │   └── templates.py          # Prompt templates
│   ├── utils/
│   │   └── security.py           # Security utilities
│   └── validators/
│       ├── input_validator.py    # Input validation
│       └── output_validator.py   # Output validation
├── frontend/
│   ├── src/
│   │   ├── App.jsx               # Main React component
│   │   ├── main.jsx              # React entry point
│   │   └── ...
│   ├── package.json
│   └── vite.config.js
├── prompts/
│   ├── current.yaml              # Active prompt configuration
│   └── v1.0.0.yaml               # Versioned prompts
└── tests/
    └── test_agent.py             # Unit tests
```

## Configuration

The application uses environment variables for configuration. Key settings include:

- `GOOGLE_API_KEY`: Your Google Gemini API key
- `GEMINI_MODEL`: Primary Gemini model to use
- `GEMINI_MODEL_FALLBACKS`: Comma-separated list of fallback models
- `ENABLE_INPUT_VALIDATION`: Enable/disable input validation
- `ENABLE_OUTPUT_VALIDATION`: Enable/disable output validation

See `app/config/settings.py` for all available configuration options.

## Development

### Running Tests

```bash
python -m pytest tests/
```

### Linting

Backend:
```bash
black .  # Format code
isort .  # Sort imports
```

Frontend:
```bash
npm run lint
```

## Security Features

- Input validation to prevent malicious queries
- Output filtering to ensure safe responses
- Security guardrails in prompts to prevent prompt injection
- PII masking capabilities
- Restricted to CloudCart-related queries only

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.