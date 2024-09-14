# MyPIA (My Personal Intelligent Assistant)

![CI](https://github.com/dodwmd/mypia/workflows/CI/badge.svg)

A personal AI assistant that uses public LLMs and a locally hosted vector database, prioritizing user data privacy.

## Features

- CLI-based interface
- Email integration (IMAP)
- Calendar integration (CalDAV)
- Task management system
- Web scraping and content processing
- GitHub integration
- Local LLM inference using llama.cpp
- Advanced text processing using LLaMA 7B model:
  - Text summarization
  - Text generation
  - Question answering
  - Task generation
  - Sentiment analysis
- Local embeddings generation using SentenceTransformers
- Vector database integration using ChromaDB

## Getting Started

### Prerequisites

- [Conda](https://docs.conda.io/en/latest/miniconda.html)
- [Poetry](https://python-poetry.org/docs/#installation)

### Setup

1. Clone the repository:
   ```
   git clone https://github.com/dodwmd/mypia.git
   cd mypia
   ```

2. Create the conda environment:
   ```
   conda env create -f config/environment.yml
   ```

3. Activate the conda environment:
   ```
   conda activate mypia
   ```

4. Install project dependencies:
   ```
   poetry install
   ```

5. Run the CLI:
   ```
   poetry run mypia
   ```

### LLM Setup

1. Download a compatible LLaMA model (e.g., LLaMA 7B) and convert it to the required format for llama.cpp.
2. Place the model file in a directory accessible to the Docker container.
3. Update the `LLM_MODEL_PATH` environment variable in the `docker-compose.yml` file to point to your model file.

## Contributing

[Add guidelines for contributing to the project]

## License

[Add your chosen license information]

## Usage

After setting up the project, you can use the following commands:

1. Summarize text:
   ```
   poetry run mypia summarize "Your long text here" --max-length 50 --format paragraph
   ```

2. Generate text:
   ```
   poetry run mypia generate "Your prompt here" --max-tokens 100 --temperature 0.7
   ```

3. Answer questions:
   ```
   poetry run mypia answer "Context information" "Your question here" --max-tokens 50
   ```

4. Generate tasks:
   ```
   poetry run mypia tasks "Project description" --num-tasks 5
   ```

5. Analyze sentiment:
   ```
   poetry run mypia sentiment "Text to analyze"
   ```

6. Generate embeddings:
   ```
   poetry run mypia embed "Your text here"
   ```

7. Compute similarity between two texts:
   ```
   poetry run mypia similarity "First text" "Second text"
   ```

8. Add a document to the vector database:
   ```
   poetry run mypia add-document "collection_name" "Your document text" --metadata '{"key": "value"}' --id "unique_id"
   ```

9. Query the vector database:
   ```
   poetry run mypia query-db "collection_name" "Your query text" --n-results 5
   ```

10. Add a document with its embedding to the vector database:
    ```
    poetry run mypia add-document-with-embedding "collection_name" "Your document text" --metadata '{"key": "value"}' --id "unique_id"
    ```

11. Query the vector database using text embedding:
    ```
    poetry run mypia query-db-with-embedding "collection_name" "Your query text" --n-results 5
    ```

12. Retrieve the embedding for a specific document:
    ```
    poetry run mypia get-embedding "collection_name" "document_id"
    ```

13. Update the embedding for a specific document:
    ```
    poetry run mypia update-document-embedding "collection_name" "document_id" "Updated document text" --metadata '{"key": "new_value"}'
    ```

14. Delete a document and its embedding from the vector database:
    ```
    poetry run mypia delete-document-embedding "collection_name" "document_id"
    ```

15. Fetch recent emails:
    ```
    poetry run mypia fetch-emails --limit 10
    ```

16. Summarize a specific email:
    ```
    poetry run mypia summarize-email <email_uid>
    ```

17. Add an email to the vector database:
    ```
    poetry run mypia add-email-to-vectordb <email_uid> "collection_name"
    ```

18. Ingest emails into the vector database:
    ```
    poetry run mypia ingest-emails "collection_name" --limit 50
    ```

19. Ingest new emails into the vector database:
    ```
    poetry run mypia ingest-new-emails "collection_name"
    ```

20. Send an email:
    ```
    poetry run mypia send-email --to "recipient@example.com" --subject "Test Email" --body "This is a test email" --cc "cc@example.com" --bcc "bcc@example.com"
    ```

21. Reply to an email:
    ```
    poetry run mypia reply-to-email <original_email_uid> --body "This is a reply to your email"
    ```

22. Forward an email:
    ```
    poetry run mypia forward-email <original_email_uid> --to "forward@example.com" --body "FYI: Forwarding this email"
    ```

23. Watch for new emails and ingest them in real-time:
    ```
    poetry run mypia watch-emails "collection_name" --interval 60
    ```

24. Summarize new emails:
    ```
    poetry run mypia summarize-new-emails --max-length 50 --limit 5
    ```

25. Watch for new emails, summarize them, and ingest them into the vector database in real-time:
    ```
    poetry run mypia watch-emails-with-summary "collection_name" --interval 60 --max-length 50
    ```

26. List available calendars:
    ```
    poetry run mypia list-calendars
    ```

27. List events in a calendar:
    ```
    poetry run mypia list-events "calendar_name" --days 7
    ```

28. Create a new event:
    ```
    poetry run mypia create-event "calendar_name" --summary "Meeting" --start "2023-06-01 14:00" --end "2023-06-01 15:00" --description "Team meeting"
    ```

29. Update an existing event:
    ```
    poetry run mypia update-event "calendar_name" "event_id" --summary "Updated Meeting" --start "2023-06-01 14:30" --end "2023-06-01 15:30"
    ```

30. Delete an event:
    ```
    poetry run mypia delete-event "calendar_name" "event_id"
    ```

31. Ingest past calendar events:
    ```
    poetry run mypia ingest-past-events "calendar_name" "collection_name" --days 30
    ```

32. Ingest future calendar events:
    ```
    poetry run mypia ingest-future-events "calendar_name" "collection_name" --days 30
    ```

33. Ingest all calendar events (past and future):
    ```
    poetry run mypia ingest-all-events "calendar_name" "collection_name" --past-days 30 --future-days 30
    ```

34. Add a calendar task:
    ```
    poetry run mypia task add-calendar-task --title "Team Meeting" --description "Weekly team sync" --start-time "2023-06-01 14:00" --end-time "2023-06-01 15:00" --location "Conference Room A"
    ```

35. Add an email task:
    ```
    poetry run mypia task add-email-task --title "Send Report" --description "Send weekly report to manager" --recipient "manager@example.com" --subject "Weekly Report" --body "Please find attached the weekly report."
    ```

36. List all tasks:
    ```
    poetry run mypia task list-tasks
    ```

37. Execute a specific task:
    ```
    poetry run mypia task execute-task <task_id>
    ```

38. Remove a specific task:
    ```
    poetry run mypia task remove-task <task_id>
    ```

39. Add a web lookup task:
    ```
    poetry run mypia task add-web-lookup-task --title "Research AI trends" --description "Look up latest AI trends" --url "https://example.com/ai-trends"
    ```

40. Add a GitHub PR review task:
    ```
    poetry run mypia task add-github-pr-review-task --title "Review PR #123" --description "Review pull request for new feature" --pr-url "https://github.com/user/repo/pull/123" --github-token "your_github_token"
    ```

41. Add a general information lookup task:
    ```
    poetry run mypia task add-general-info-lookup-task --title "Weather forecast" --description "Get weather forecast for the week" --query "What's the weather forecast for New York City this week?"
    ```

42. Scrape content from a web page:
    ```
    poetry run mypia scrape-web "https://example.com" --summarize
    ```

43. Process and analyze a web page:
    ```
    poetry run mypia web process-url "https://example.com"
    ```

44. Compare two web pages:
    ```
    poetry run mypia web compare-urls "https://example1.com" "https://example2.com"
    ```

45. Analyze a topic by processing multiple web pages:
    ```
    poetry run mypia web analyze-topic "artificial intelligence" --num-urls 5
    ```

46. Review a GitHub Pull Request:
    ```
    poetry run mypia github review-pr "owner/repo" 123
    ```

47. Get details of a GitHub Pull Request:
    ```
    poetry run mypia github get-pr-details "owner/repo" 123
    ```

48. List issues in a GitHub repository:
    ```
    poetry run mypia github list-issues "owner/repo" --state open
    ```

49. Create a new issue in a GitHub repository:
    ```
    poetry run mypia github create-issue "owner/repo" --title "New issue" --body "Issue description"
    ```

50. Get statistics for a GitHub repository:
    ```
    poetry run mypia github repo-stats "owner/repo"
    ```

51. Review a GitHub Pull Request with action log parsing and fix suggestions:
    ```
    poetry run mypia github review-pr-with-fixes "owner/repo" 123
    ```

52. Review a GitHub Pull Request with automated updates and responses:
    ```
    poetry run mypia github review-pr-with-automation "owner/repo" 123
    ```

53. Create a new user:
    ```
    poetry run mypia db create-user --username "john_doe" --email "john@example.com"
    ```

54. Create a new task for a user:
    ```
    poetry run mypia db create-task 1 --title "Complete project" --description "Finish the AI assistant project"
    ```

55. Update the status of a task:
    ```
    poetry run mypia db update-task-status 1 completed
    ```

56. Set a user preference:
    ```
    poetry run mypia db set-preference 1 --key "theme" --value "dark"
    ```

57. Get a user preference:
    ```
    poetry run mypia db get-preference 1 theme
    ```

58. Get a user:
    ```
    poetry run mypia db get-user <user_id>
    ```

59. Update a user:
    ```
    poetry run mypia db update-user <user_id> --username "new_username" --email "new_email@example.com"
    ```

60. Delete a user:
    ```
    poetry run mypia db delete-user <user_id>
    ```

61. Get a task:
    ```
    poetry run mypia db get-task <task_id>
    ```

62. Update a task:
    ```
    poetry run mypia db update-task <task_id> --title "New title" --status "in_progress"
    ```

63. Delete a task:
    ```
    poetry run mypia db delete-task <task_id>
    ```

64. List user tasks:
    ```
    poetry run mypia db list-user-tasks <user_id> --status "pending"
    ```

65. Set a user preference:
    ```
    poetry run mypia db set-preference <user_id> --key "theme" --value "dark"
    ```

66. Get a user preference:
    ```
    poetry run mypia db get-preference <user_id> theme
    ```

67. Delete a user preference:
    ```
    poetry run mypia db delete-preference <user_id> theme
    ```

68. Delete all user preferences:
    ```
    poetry run mypia db delete-all-preferences <user_id>
    ```

69. Log an email:
    ```
    poetry run mypia db log-email <user_id> --subject "Meeting reminder" --sender "boss@example.com" --recipient "john@example.com" --is_sent false
    ```

70. Get email logs:
    ```
    poetry run mypia db get-email-logs <user_id> --limit 5
    ```

71. Set a user preference:
    ```
    poetry run mypia preferences set-preference <user_id> <key> <value>
    ```

72. Get a user preference:
    ```
    poetry run mypia preferences get-preference <user_id> <key>
    ```

73. List all preferences for a user:
    ```
    poetry run mypia preferences list-preferences <user_id>
    ```

74. Delete a user preference:
    ```
    poetry run mypia preferences delete-preference <user_id> <key>
    ```

75. Delete all preferences for a user:
    ```
    poetry run mypia preferences delete-all-preferences <user_id>
    ```

76. Start Celery worker:
    ```
    poetry run mypia celery start-worker
    ```

77. Start Celery beat scheduler:
    ```
    poetry run mypia celery start-beat
    ```

78. Manually trigger email checking task:
    ```
    poetry run mypia celery check-emails
    ```

79. Manually trigger calendar sync task:
    ```
    poetry run mypia celery sync-calendar
    ```

80. Analyze text using spaCy:
        poetry run mypia nlp analyze "Your text goes here"
    ```

81. Extract named entities from text:
    ```
    poetry run mypia nlp entities "Apple Inc. was founded by Steve Jobs in Cupertino, California."
    ```

82. Extract noun chunks from text:
    ```
    poetry run mypia nlp noun-chunks "The quick brown fox jumps over the lazy dog."
    ```

83. Extract sentences from text:
    ```
    poetry run mypia nlp sentences "This is the first sentence. This is the second one. And here's the third!"
    ```

84. Find similar words:
    ```
    poetry run mypia nlp similar-words "computer" --n 5
    ```

85. Get word vector:
    ```
    poetry run mypia nlp word-vector "artificial"
    ```

48. List issues in a GitHub repository:
    ```
    poetry run mypia github list-issues "owner/repo" --state open
    ```
