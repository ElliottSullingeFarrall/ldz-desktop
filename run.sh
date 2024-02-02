export POETRY_VIRTUALENVS_IN_PROJECT=true

export FLASK_APP="source"
export FLASK_DEBUG=1
export FLASK_RUN_PORT=4040

poetry env use $(which python)
poetry install --no-root
poetry run flask run