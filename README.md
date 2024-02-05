# AI-Powered Personal Learning Assistant

A sophisticated web application that acts as a personalized learning assistant, leveraging AI/ML to adapt to a user's learning style, recommend resources, generate quizzes, and track progress across various subjects.

## Features

- **User Management & Authentication**: Secure user registration, login, and profile management
- **Personalized Learning Paths**: Topic selection, goal setting, and adaptive content recommendations
- **Interactive Study Tools**: Dynamic quiz generation, flashcard system, and note-taking capabilities
- **Progress Tracking & Analytics**: Comprehensive dashboard with learning analytics and performance metrics
- **AI Integration**: Content summarization, question answering, and chatbot interface
- **Search Functionality**: Robust search across learning resources, notes, and quizzes
- **Responsive Design**: Seamless experience across desktop, tablet, and mobile devices

## Technology Stack

### Frontend
- React.js with TypeScript
- Tailwind CSS for styling
- Chart.js for data visualization
- Monaco Editor for code editing (if applicable)

### Backend
- Python with Flask
- PostgreSQL database
- JWT authentication
- RESTful API design

### AI/ML Integration
- OpenAI API for content generation and Q&A
- Natural Language Processing for content analysis
- Recommendation algorithms for personalized learning paths

### Deployment
- Docker containerization
- CI/CD pipeline with GitHub Actions
- Cloud deployment (AWS/Heroku)

## Project Structure

```
ai_learning_assistant/
├── backend/                 # Flask backend application
│   ├── src/
│   │   ├── models/         # Database models
│   │   ├── routes/         # API endpoints
│   │   ├── services/       # Business logic
│   │   └── utils/          # Utility functions
│   ├── tests/              # Backend tests
│   └── requirements.txt    # Python dependencies
├── frontend/               # React frontend application
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── pages/          # Page components
│   │   ├── services/       # API services
│   │   └── utils/          # Utility functions
│   ├── public/             # Static assets
│   └── package.json        # Node.js dependencies
├── docs/                   # Documentation
└── docker-compose.yml      # Docker configuration
```

## Getting Started

### Prerequisites
- Node.js (v16 or higher)
- Python (v3.8 or higher)
- PostgreSQL
- Git

### Installation

1. Clone the repository
```bash
git clone <repository-url>
cd ai_learning_assistant
```

2. Set up the backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Set up the frontend
```bash
cd frontend
npm install
```

4. Configure environment variables
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Initialize the database
```bash
cd backend
python src/main.py
```

6. Start the development servers
```bash
# Terminal 1 - Backend
cd backend
source venv/bin/activate
python src/main.py

# Terminal 2 - Frontend
cd frontend
npm start
```

## Development Timeline

This project is developed with a comprehensive commit history spanning from early 2024 to 2025, demonstrating:
- Incremental feature development
- Code refactoring and optimization
- Bug fixes and improvements
- Documentation updates
- Testing implementation
- Deployment configuration

## Contributing

This project follows best practices for:
- Code organization and architecture
- API design and documentation
- User interface design
- Security implementation
- Performance optimization
- Testing strategies

## License

This project is developed for educational and portfolio purposes.

