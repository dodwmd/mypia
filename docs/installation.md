---
layout: page
title: Installation
nav_order: 2
---

# Installation

## Prerequisites

Before installing MyPIA, ensure you have the following prerequisites:

- Python 3.9 or higher
- Poetry
- Conda (optional, but recommended for environment management)

## Installation Steps

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/mypia.git
   cd mypia
   ```

2. Create a Conda environment (optional but recommended):

   ```bash
   conda create -n mypia python=3.9
   conda activate mypia
   ```

3. Install the project dependencies using Poetry:

   ```bash
   poetry install
   ```

4. Set up the environment variables:

   Create a `.env` file in the project root directory and add the following variables:

   ```
   EMAIL_HOST=your_email_host
   EMAIL_USERNAME=your_email_username
   EMAIL_PASSWORD=your_email_password
   SMTP_HOST=your_smtp_host
   CALDAV_URL=your_caldav_url
   CALDAV_USERNAME=your_caldav_username
   CALDAV_PASSWORD=your_caldav_password
   DATABASE_URL=sqlite:///./mypia.db
   REDIS_URL=redis://localhost:6379/0
   GITHUB_TOKEN=your_github_token
   ENCRYPTION_PASSWORD=your_encryption_password
   ```

   Replace the placeholder values with your actual configuration details.

5. Initialize the database:

   ```bash
   poetry run python -c "from personal_ai_assistant.database.models import init_db; init_db('sqlite:///./mypia.db')"
   ```

6. Download the required language model:

   ```bash
   poetry run python -m spacy download en_core_web_sm
   ```

Your MyPIA installation is now complete and ready to use!
