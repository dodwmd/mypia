# Development Prompts for Personal AI Assistant

## 1. Project Setup
- Create a basic project structure for a Python CLI application using Click.
- Set up a Docker environment with Docker Compose for the application and its dependencies.
- Implement a configuration system using python-dotenv and pydantic.
- Initialize a Git repository and set up GitHub integration.
- Set up conda and poetry for environment and dependency management.

## 2. LLM Integration
- Integrate llama.cpp for local LLM inference.
- Implement a module for text generation and summarization using the LLaMA 7B model.

## 3. Embeddings and Vector Database
- Set up SentenceTransformers for local embeddings generation.
- Integrate ChromaDB as the vector database.
- Create functions to store and retrieve embeddings from ChromaDB.

## 4. Email Integration
- Implement email fetching and parsing using imapclient.
- Create functions to ingest emails into the vector database.
- Develop a module to send, reply to, and forward emails.
- Implement real-time ingestion of new emails.
- Create a function to summarize new emails using the LLM.

## 5. Calendar Integration
- Integrate the caldav library for calendar operations.
- Implement functions to fetch, create, update, and delete calendar events.
- Create functions to ingest past and future events into the vector database.

## 6. Task Management System
- Design and implement a modular task management system using custom Python classes.
- Create base classes and interfaces for different types of tasks.
- Implement task types for calendar management, web content lookup, GitHub PR review, email operations, and general information lookup.

## 7. Web Scraping and Content Processing
- Implement web scraping functionality using trafilatura.
- Create a module to extract, process, and summarize web content.

## 8. GitHub Integration
- Integrate PyGithub for GitHub API interactions.
- Implement functions to review PRs, parse action logs, and suggest fixes.
- Develop automated PR update and response capabilities.

## 9. Async Operations
- Refactor key I/O-bound operations to use asyncio for better performance.

## 10. Data Persistence
- Set up SQLite with SQLAlchemy for storing non-vector data.
- Implement data models and CRUD operations for persistent storage.
- Create functions for storing and retrieving user preferences.

## 11. Task Queue
- Integrate Celery with Redis for background task processing and scheduling.
- Implement background tasks for email checking, calendar syncing, etc.

## 12. CLI Enhancements
- Use the rich library to improve CLI output formatting and user experience.

## 13. Natural Language Processing
- Integrate spaCy for additional NLP tasks beyond LLM capabilities.

## 14. Security and Error Handling
- Implement secure handling of sensitive data (e.g., API keys, passwords).
- Set up comprehensive error handling and logging.
- Implement end-to-end encryption for data at rest and in transit.

## 15. Testing
- Write unit tests using pytest for core functionalities.
- Implement integration tests for component interactions.
- Set up end-to-end tests for complete workflows.
- Configure pytest-cov for code coverage reporting.
- Set up mypy for static type checking.

## 16. Documentation
- Create comprehensive documentation for the project, including setup instructions, usage guide, and API references using Sphinx.
- Document the development approach and coding standards (PEP 8 and Google style guide).
- Using Jekyll, create a website for the documentation. Use the theme just-the-docs and the documentation should be hosted on github pages. Use the plugins jekyll-redirect-from, jekyll-feed and jekyll-sitemap.

## 17. Containerization
- Finalize the Docker setup, including multi-stage builds for optimization.
- Create a docker-compose.yml file to orchestrate all services.

## 18. Nginx Configuration
- Set up Nginx as a reverse proxy and load balancer for the services.

## 19. Offline Capabilities
- Implement core functionalities to work offline.
- Develop a synchronization mechanism for when internet connection is restored.

## 20. Performance Optimization
- Implement caching strategies for frequently accessed data.
- Set up performance profiling using cProfile and memory_profiler.

## 21. Updates and Maintenance
- Develop an automated update mechanism for LLM models, embeddings, and system components.
- Implement backup and recovery procedures for user data.

## 22. Scalability
- Design the system for single-user deployment with considerations for potential multi-user scaling.

Remember to approach these prompts iteratively, focusing on core functionalities first and gradually expanding the feature set. Regularly review and refactor the code to maintain quality and readability throughout the development process.
