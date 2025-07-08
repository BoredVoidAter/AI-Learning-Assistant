# 🎓 AI-Powered Personal Learning Assistant

A comprehensive full-stack web application that revolutionizes personal learning through AI-powered features, gamification, and advanced analytics.

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![React](https://img.shields.io/badge/React-18.0+-61DAFB.svg)
![Flask](https://img.shields.io/badge/Flask-2.3+-000000.svg)
![SQLite](https://img.shields.io/badge/SQLite-3.0+-003B57.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## 🌟 Features

### 🎯 Core Learning Features
- **Personalized Learning Paths**: AI-generated learning paths tailored to individual goals and skill levels
- **Interactive Quiz System**: Comprehensive quiz platform with multiple question types and adaptive difficulty
- **Resource Management**: Curated learning resources with AI-powered content generation
- **Advanced Note-Taking**: Sophisticated note-taking system with tagging and search capabilities

### 🎮 Gamification Engine
- **Achievement System**: 12+ achievements across multiple categories with rarity levels
- **Badge Collection**: Visual badges for specific accomplishments and milestones
- **Level Progression**: Exponential XP system with automatic level-ups
- **Leaderboards**: Weekly, monthly, and all-time rankings across different categories
- **Streak Tracking**: Learning streak monitoring for consistent engagement

### 📊 Analytics & Insights
- **Learning Progress Tracking**: Detailed progress analytics with visual charts
- **Quiz Performance Analysis**: Comprehensive performance metrics and trends
- **Study Time Analytics**: Time tracking with daily, weekly, and monthly breakdowns
- **Interactive Dashboards**: Beautiful data visualizations using Recharts

### 🔍 Advanced Features
- **Global Search**: Unified search across all content types with intelligent relevance scoring
- **Feedback System**: Comprehensive feedback and bug reporting mechanism
- **AI Integration**: Content generation and personalized recommendations
- **User Activity Tracking**: Detailed activity logs and user behavior analytics

## 🏗️ Technical Architecture

### Backend Stack
- **Framework**: Flask (Python 3.11+)
- **Database**: SQLite with SQLAlchemy ORM
- **Authentication**: JWT-based authentication
- **API Design**: RESTful API with comprehensive endpoints

### Frontend Stack
- **Framework**: React 18 with modern hooks
- **Styling**: Tailwind CSS + Shadcn/UI components
- **Icons**: Lucide React icons
- **Charts**: Recharts for data visualization
- **Routing**: React Router for SPA navigation

### Key Features Implementation
- **Modular Architecture**: Organized codebase with separation of concerns
- **Security**: JWT authentication, input validation, CORS configuration
- **Performance**: Optimized queries, efficient state management
- **Responsive Design**: Mobile-first approach with Tailwind CSS

## 🚀 Quick Start

### Prerequisites
- Python 3.11 or higher
- Node.js 20 or higher
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/BoredVoidAter/AI-Learning-Assistant.git
   cd AI-Learning-Assistant
   ```

2. **Backend Setup**
   ```bash
   cd backend
   
   # Create virtual environment
   python -m venv venv
   
   # Activate virtual environment
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   
   # Install dependencies
   pip install flask flask-cors flask-jwt-extended sqlalchemy python-dotenv
   
   # Run the backend server
   python src/main.py
   ```

3. **Frontend Setup**
   ```bash
   cd frontend
   
   # Install dependencies
   npm install
   
   # Start the development server
   npm run dev
   ```

4. **Access the Application**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:5000

### Environment Variables

Create a `.env` file in the backend directory:
```env
SECRET_KEY=your-secret-key-here
FLASK_ENV=development
DATABASE_URL=sqlite:///app.db
```

## 📱 Usage Guide

### Getting Started
1. **Register**: Create a new account or login with existing credentials
2. **Explore**: Browse the dashboard to see your learning analytics
3. **Learn**: Start with learning paths or take quizzes to test your knowledge
4. **Track Progress**: Monitor your progress through the analytics dashboard
5. **Earn Achievements**: Complete activities to unlock achievements and badges

### Key Workflows

#### Creating Learning Content
- Navigate to Learning Paths to create custom learning paths
- Add resources and organize them by topics
- Create quizzes to test knowledge retention

#### Tracking Progress
- View detailed analytics in the Dashboard
- Monitor learning streaks and study time
- Check leaderboards to see your ranking

#### Using Gamification
- Visit the Achievements page to see available achievements
- Collect badges by completing specific milestones
- Compete on leaderboards with other learners

## 🎯 Project Highlights

### Development Metrics
- **32+ Git Commits**: Demonstrating consistent development progress
- **15+ Database Models**: Comprehensive data modeling for complex relationships
- **25+ API Endpoints**: RESTful API covering all application functionality
- **10+ React Components**: Modular frontend architecture
- **5+ Service Classes**: Business logic separation and organization

### Technical Achievements
- **Full-Stack Integration**: Seamless communication between React frontend and Flask backend
- **Complex Database Relationships**: Advanced SQLAlchemy relationships and queries
- **Real-time Features**: Dynamic updates and interactive user interfaces
- **Security Implementation**: JWT authentication and input validation
- **Performance Optimization**: Efficient queries and optimized frontend rendering

### Code Quality
- **Modular Architecture**: Well-organized codebase with clear separation of concerns
- **Error Handling**: Comprehensive error handling and user feedback
- **Documentation**: Detailed code comments and API documentation
- **Best Practices**: Following industry standards for both backend and frontend development

## 📊 Database Schema

### Core Models
- **User**: Authentication and profile management
- **LearningPath**: Educational content organization
- **Quiz/Question**: Assessment system
- **Achievement/Badge**: Gamification elements
- **UserActivity**: Activity tracking and analytics

### Relationships
- One-to-many relationships between users and their content
- Many-to-many relationships for complex associations
- Foreign key constraints ensuring data integrity

## 🔧 API Documentation

### Authentication
```
POST /api/auth/register    # User registration
POST /api/auth/login       # User login
GET  /api/auth/profile     # Get user profile
```

### Learning Content
```
GET    /api/learning-paths           # List learning paths
POST   /api/learning-paths           # Create learning path
GET    /api/learning-paths/{id}      # Get specific learning path
PUT    /api/learning-paths/{id}      # Update learning path
DELETE /api/learning-paths/{id}      # Delete learning path
```

### Gamification
```
GET /api/gamification/profile        # User gamification profile
GET /api/gamification/achievements   # List achievements
GET /api/gamification/badges         # List badges
GET /api/gamification/leaderboard/{type}/{category}  # Leaderboards
```

### Analytics
```
GET /api/analytics/dashboard         # Dashboard data
GET /api/analytics/learning-progress # Learning progress
GET /api/analytics/quiz-analytics    # Quiz performance
```

## 🤝 Contributing

This project demonstrates advanced full-stack development skills and is designed to showcase professional-level software engineering capabilities. The codebase follows industry best practices and is structured for maintainability and scalability.

### Development Guidelines
- Follow the existing code structure and naming conventions
- Write comprehensive commit messages
- Ensure proper error handling and validation
- Maintain consistent styling and formatting

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🎯 Project Goals

This project was developed to demonstrate:
- **Full-Stack Development Skills**: Comprehensive understanding of both frontend and backend technologies
- **Database Design**: Complex relational database modeling and optimization
- **API Development**: RESTful API design and implementation
- **Modern Frontend Development**: React with modern patterns and best practices
- **Software Engineering**: Clean code, modular architecture, and professional development practices
- **Problem Solving**: Complex feature implementation and system integration

## 📞 Contact

For questions about this project or potential collaboration opportunities, please feel free to reach out through the GitHub repository.

---

**Built with ❤️ using Flask, React, and modern web technologies**

