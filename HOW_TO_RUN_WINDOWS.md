# How to Run the AI Learning Assistant on Windows

This guide will walk you through setting up and running the AI Learning Assistant project on your Windows machine. The project consists of a Flask backend and a React frontend.

## Prerequisites

Before you begin, ensure you have the following installed:

1.  **Git:** Download and install from [git-scm.com](https://git-scm.com/download/win).
2.  **Python 3.9+:** Download and install from [python.org](https://www.python.org/downloads/windows/). Make sure to check "Add Python to PATH" during installation.
3.  **Node.js (LTS version):** Download and install from [nodejs.org](https://nodejs.org/en/download/). This will also install npm (Node Package Manager).
4.  **pnpm (optional, but recommended for frontend):** After installing Node.js, open PowerShell or Command Prompt as Administrator and run:
    ```bash
    npm install -g pnpm
    ```

## Setup Steps

### 1. Clone the Repository

Open your Git Bash, PowerShell, or Command Prompt and clone the project repository:

```bash
cd C:\your\desired\directory
git clone https://github.com/BoredVoidAter/AI-Learning-Assistant.git
cd AI-Learning-Assistant
```

### 2. Backend Setup (Flask)

Navigate to the `backend` directory and set up the Flask application.

```bash
cd backend
```

#### Create and Activate a Virtual Environment

It's highly recommended to use a virtual environment to manage dependencies.

```bash
python -m venv venv
.\venv\Scripts\activate
```

#### Install Backend Dependencies

```bash
pip install -r requirements.txt
```

#### Set Environment Variables

You need to set a `SECRET_KEY` for Flask and an `OPENAI_API_KEY` for the AI features. You can create a `.env` file in the `backend` directory or set them directly in your environment.

**Option A: Using a `.env` file (recommended for development)**

Create a file named `.env` in the `backend` directory with the following content:

```
SECRET_KEY="your_very_secret_key_here"
OPENAI_API_KEY="your_openai_api_key_here"
```

**Option B: Setting directly in PowerShell (temporary for current session)**

```powershell
$env:SECRET_KEY="your_very_secret_key_here"
$env:OPENAI_API_KEY="your_openai_api_key_here"
```

#### Initialize Database

The project uses SQLite. The database will be created automatically when the app runs for the first time.

#### Run the Flask Backend

```bash
flask run --host=0.0.0.0 --port=5000
```

The backend server should now be running at `http://localhost:5000`.

### 3. Frontend Setup (React)

Open a **new** Git Bash, PowerShell, or Command Prompt window. Navigate to the `frontend` directory.

```bash
cd C:\your\desired\directory\AI-Learning-Assistant\frontend
```

#### Install Frontend Dependencies

```bash
pnpm install
# or npm install
```

#### Set Environment Variables

Create a `.env` file in the `frontend` directory to point to your backend API.

```
VITE_API_URL=http://localhost:5000/api
```

#### Run the React Frontend

```bash
pnpm dev
# or npm run dev
```

The frontend development server should now be running, typically at `http://localhost:5173` (check the output in your terminal for the exact URL).

## Usage

Open your web browser and navigate to the frontend URL (e.g., `http://localhost:5173`). You should be able to register a new user, log in, and start using the AI Learning Assistant.

If you encounter any issues, double-check the environment variables, ensure both backend and frontend servers are running, and verify that the API URL in the frontend `.env` file matches your backend address.


