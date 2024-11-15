
# Jira Copilot Backend

![Jira FStack Logo](artefacts/genai_jira.JPG)

## Overview

**Jira Copilot Backend** is a FastAPI web application designed to assist Agile teams in estimating Jira stories using the story's summary and description using OpenAI ChatGPT. Additionally, it provides functionality to create and update subtasks directly on the Jira board, streamlining project management and enhancing productivity.

## 🚀 Explore the App

🌐 **Webapp Link:** [Click Here to Access the Jira Estimator](https://jira-copilot.vercel.app/) [(Contributed by Rishav)](https://github.com/rishavmahapatra/Jira-Copilot)

📄 **Swagger Documentation:** [Click Here for API Docs](https://jira-fstack-app-1.onrender.com/docs#/)


## Features

- **GenAI Story Estimation**: Estimate the effort required for Jira stories based on the summary and description automatically fetched based on story-id.
- **Automated Subtask Creation in Jira board**: Create subtasks in Jira for any given story ID.

## Getting Started

### Prerequisites

- Python 3.10 or higher
- A Jira account with API access & keys
- A OpenAI API key

### Installation

1. **Clone the repository**:

   ```bash
   git clone https://github.com/yourusername/jira_fstack_app.git
   cd jira_fstack_app
   ```

2. **Create a virtual environment**:

   ```bash
   python -m venv venv
   source venv/bin/activate   # On Windows use `venv\Scripts\activate`
   ```

3. **Install the required packages**:

   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:

   Create a `.env` file in the root of the project with the following content:

   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   ```

   Replace `your_openai_api_key_here` with your actual OpenAI API key.

### Running the Application

To run the FastAPI application, execute the following command:

```bash
uvicorn main:app --reload
```

You can access the API documentation at [http://localhost:8000/docs](http://localhost:8000/docs).

### API Endpoints

- **Health Check**
  - `GET /health`
  - Returns the health status of the application.

- **Estimate Story**
  - `POST /story_id`
  - Request body should include the story information.
  - Requires headers: `username`, `api_token`, `jira_url`.
  - Additionally you can pass customised prompt overriding the existing prompt

- **Create Subtasks**
  - `POST /create_subtasks`
  - Request body should include estimated story information.
  - Requires headers: `username`, `api_token`, `jira_url`.

## Contributors
- Bijon - Python & Backend
- [Rishav](https://github.com/rishavmahapatra) - Frontend
- [Jaiyesh](https://github.com/jaiyesh) - Python & Backend
  
## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue to discuss any improvements or features.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
