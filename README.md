# YouTube Video Downloader
A full-stack application to download YouTube videos, featuring a FastAPI backend and a Vue.js frontend.

## Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
  - [Backend Setup](#backend-setup)
  - [Frontend Setup](#frontend-setup)
- [Usage](#usage)
  - [Running the Backend](#running-the-backend)
  - [Running the Frontend](#running-the-frontend)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [License](#license)

## Features

- Download YouTube videos in various formats.
- User-friendly interface built with Vue.js.
- RESTful API powered by FastAPI.
- Integrated unit testing for backend.
- Responsive design with TailwindCSS.

## Prerequisites

- **Python 3.12**
- **Node.js** (v14 or later)
- **pip**
- **npm or yarn**

## Installation

### Backend Setup

1. **Navigate to the backend directory:**

   ```bash
   cd backend
   ```

2. **Create a virtual environment:**

   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment:**

   - On macOS:
     ```bash
     source venv/bin/activate
     ```

4. **Install the required dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

### Frontend Setup

1. **Navigate to the frontend directory:**

   ```bash
   cd frontend
   ```

2. **Install the required dependencies:**

   ```bash
   npm install
   ```

## Usage

### Running the Backend

1. **Ensure the virtual environment is activated:**

   ```bash
   source backend/venv/bin/activate
   ```

2. **Start the FastAPI server with Uvicorn:**

   ```bash
   uvicorn main:app --reload
   ```

   The backend API will be available at [http://localhost:8000](http://localhost:8000).

### Running the Frontend

1. **Navigate to the frontend directory:**

   ```bash
   cd frontend
   ```

2. **Start the development server:**

   ```bash
   npm run dev
   ```

   The frontend will be available at [http://localhost:3000](http://localhost:3000).

## Contributing

1. **Fork the repository.**

2. **Create a new branch:**

   ```bash
   git checkout -b feature/YourFeature
   ```

3. **Commit your changes:**

   ```bash
   git commit -m "Add some feature"
   ```

4. **Push to the branch:**

   ```bash
   git push origin feature/YourFeature
   ```

5. **Open a pull request.**

## License

This project is licensed under the [MIT License](License).