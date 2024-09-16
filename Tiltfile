# Load the docker-compose file
docker_compose('./docker-compose.yml')

# Define the Docker build
docker_build(
    'mypia-app',
    '.',
    dockerfile='Dockerfile',
    build_args={'PYTHON_VERSION': '3.9'},
    live_update=[
        sync('.', '/app'),
        run('poetry install', trigger=['./pyproject.toml', './poetry.lock']),
    ]
)

# Define resources for each service
dc_resource('nginx', labels=["web"])
dc_resource('app', labels=["app"], image='mypia-app')
dc_resource('db', labels=["db"])
dc_resource('redis', labels=["cache"])
dc_resource('celery_worker', labels=["worker"], image='mypia-celery_beat')
dc_resource('celery_beat', labels=["scheduler"], image='mypia-celery_worker')
dc_resource('chroma_db', labels=["vector_db"])

# Configure file watching
watch_file('./docker-compose.yml')
watch_file('./Dockerfile')
watch_file('./pyproject.toml')
watch_file('./poetry.lock')

# Add a resource for running tests
local_resource(
    'run-tests',
    cmd='poetry run pytest',
    labels=["testing"],
    deps=['./tests']
)

# Add a resource for linting
local_resource(
    'lint',
    cmd='poetry run flake8',
    labels=["testing"],
    deps=['.']
)

# Add a resource for the frontend development server
local_resource(
    'frontend-dev',
    serve_cmd='cd frontend && npm run dev',
    labels=["frontend"],
    deps=['./frontend/src', './frontend/app']
)
