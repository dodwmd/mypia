Usage
=====

MyPIA provides a command-line interface (CLI) for interacting with various features. Here are some example commands:

Text Processing
---------------

Summarize text:

.. code-block:: bash

   poetry run mypia summarize "Your long text here" --max-length 50 --format paragraph

Generate text:

.. code-block:: bash

   poetry run mypia generate "Your prompt here" --max-tokens 100 --temperature 0.7

Answer questions:

.. code-block:: bash

   poetry run mypia answer "Context information" "Your question here" --max-tokens 50

Email Management
----------------

Fetch recent emails:

.. code-block:: bash

   poetry run mypia fetch-emails --limit 10

Send an email:

.. code-block:: bash

   poetry run mypia send-email --to "recipient@example.com" --subject "Test Email" --body "This is a test email"

Calendar Management
-------------------

List events in a calendar:

.. code-block:: bash

   poetry run mypia list-events "calendar_name" --days 7

Create a new event:

.. code-block:: bash

   poetry run mypia create-event "calendar_name" --summary "Meeting" --start "2023-06-01 14:00" --end "2023-06-01 15:00" --description "Team meeting"

Task Management
---------------

Add a task:

.. code-block:: bash

   poetry run mypia task add-calendar-task --title "Team Meeting" --description "Weekly team sync" --start-time "2023-06-01 14:00" --end-time "2023-06-01 15:00"

List tasks:

.. code-block:: bash

   poetry run mypia task list-tasks

For a complete list of available commands and their options, run:

.. code-block:: bash

   poetry run mypia --help
