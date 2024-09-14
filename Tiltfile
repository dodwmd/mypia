# Load the docker-compose file
docker_compose('./docker-compose.yml')

# Define resources for each service
dc_resource('nginx', labels=["web"])
dc_resource('app', labels=["app"])
dc_resource('db', labels=["db"])
dc_resource('redis', labels=["cache"])
dc_resource('celery_worker', labels=["worker"])
dc_resource('celery_beat', labels=["scheduler"])
dc_resource('chroma_db', labels=["vector_db"])

# Live update for the app service
docker_build('mypia_app', '.',
    build_args={'PYTHON_VERSION': '3.9'},
    dockerfile='Dockerfile',
    live_update=[
        sync('.', '/app'),
        run('poetry install', trigger=['./pyproject.toml', './poetry.lock']),
    ]
)

# Configure file watching
watch_file('./docker-compose.yml')
watch_file('./Dockerfile')
watch_file('./pyproject.toml')
watch_file('./poetry.lock')

# Add a resource for running tests
local_resource(
    'run-tests',
    cmd='poetry run pytest',
    deps=['./tests']
)

# Add a resource for linting
local_resource(
    'lint',
    cmd='poetry run flake8',
    deps=['.']
)
