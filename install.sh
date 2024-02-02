export POETRY_VIRTUALENVS_IN_PROJECT=true

poetry env use $(which python)
poetry install --no-root