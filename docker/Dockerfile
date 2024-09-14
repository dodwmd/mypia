FROM continuumio/miniconda3:latest

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    && rm -rf /var/lib/apt/lists/*

# Copy environment.yml and create conda environment
COPY config/environment.yml .
RUN conda env create -f environment.yml

# Install poetry
RUN conda run -n mypia pip install poetry==1.4.2

# Copy pyproject.toml and poetry.lock* (if exists)
COPY pyproject.toml poetry.lock* ./

# Install project dependencies
RUN conda run -n mypia poetry config virtualenvs.create false \
    && conda run -n mypia poetry install --no-interaction --no-ansi

# Copy the rest of the application code
COPY . .

# Set the entrypoint to run the CLI
ENTRYPOINT ["conda", "run", "--no-capture-output", "-n", "mypia", "poetry", "run", "mypia"]
