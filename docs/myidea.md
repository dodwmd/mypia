# Personal AI Assistant

## Overview
This project aims to create a personal AI assistant that uses public LLMs and a locally hosted vector database. The assistant will prioritize user data privacy by using local copies of embeddings and vector databases, minimizing reliance on SaaS solutions.

## Author

Name: Michael Dodwell
Email: michael@dodwell.us
Github: https://github.com/dodwmd/mypia

## Core Functionality
1. CLI-based interface (with future plans for API and web interface)
2. Email integration (IMAP)
3. Calendar integration (CalDAV)
4. Task management system
5. Web scraping and content processing
6. GitHub integration

## Technical Stack

### Core
- Python 3.9+
- Click for CLI interface
- Docker and Docker Compose
- dotenv
- conda
- poetry
- git (github)

### LLM
- llama.cpp for local LLM inference
- Model: LLaMA 7B (adjustable based on performance requirements)

### Embeddings
- SentenceTransformers for local embeddings generation

### Vector Database
- ChromaDB (local installation)

### Email
- imapclient for IMAP integration

### Calendar
- caldav library for CalDAV support (compatible with Google Calendar and others)

### Task Queue
- Celery with Redis as a broker

### Data Persistence
- SQLite for non-vector data
- SQLAlchemy as ORM

### Web Scraping
- trafilatura for content extraction

### NLP
- spaCy for additional NLP tasks

### CLI Enhancements
- rich library for improved formatting and output

### Utilities
- python-dotenv
- pydantic

### Testing
- pytest, pytest-cov, pytest-mock
- mypy, black, flake8

### Documentation
- sphinx

### Coding Standards
- PEP 8
- Google style guide

### Deployment
- Docker for containerization
- Nginx for routing and load balancing

## Detailed Requirements

### Email Integration
- Support multiple IMAP providers
- Fetch and ingest all existing emails into the vector database
- Real-time ingestion of new emails
- Summarize new emails using LLM

### Calendar Integration
- Support CalDAV protocol (compatible with Google Calendar and others)
- Fetch and ingest past and future events into the vector database
- Create, update, and delete events

### Task Management
- Modular system for defining and executing tasks
- Support for single tasks and task sequences
- Task types include:
  - Calendar management
  - Web content lookup and summarization
  - GitHub PR review and interaction
  - Email operations (reply, send, forward)
  - General information lookup (weather, time, calculations)

### GitHub Integration
- PR review functionality
- Action log parsing and analysis
- Automated PR updates and responses

### Authentication
- Secure storage of credentials for various services (email, calendar, GitHub)
- Use of environment variables and secure vaults for sensitive data

### Data Retention and Privacy
- Configurable data retention policies for emails, calendar events, and other data
- Local storage of all data to ensure privacy

### User Preferences
- Configurable settings for LLM behavior, task priorities, and system preferences
- Storage of user preferences in local database

### Error Handling and Logging
- Comprehensive error handling with user-friendly messages
- Detailed logging of system activities and user interactions

### Performance and Scalability
- Designed for single-user deployment with potential for multi-user scaling
- Asynchronous operations for improved performance
- Caching strategies for frequently accessed data

### Security
- End-to-end encryption for data at rest and in transit
- Regular security audits and updates

### Updates and Maintenance
- Automated update mechanism for LLM models, embeddings, and system components
- Backup and recovery procedures for user data

### Offline Capabilities
- Core functionalities available offline
- Synchronization mechanism for when internet connection is restored

## Development Approach
1. Iterative development focusing on core functionalities first
2. Comprehensive testing at unit, integration, and end-to-end levels
3. Regular code reviews and refactoring to maintain code quality
4. Documentation of API, setup process, and user guide

## Deployment
- All components containerized using Docker
- docker-compose.yml for orchestrating services
- Nginx as reverse proxy and load balancer
- Minimal exposed ports for security

This comprehensive plan covers the core functionality, technical stack, and detailed requirements for the personal AI assistant. It addresses the previously missing information and provides a solid foundation for development.
