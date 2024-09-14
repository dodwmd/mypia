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
