export POETRY_VIRTUALENVS_IN_PROJECT=true

poetry env use $(which python)
poetry install --no-root

if [ ! -f config.py ]; then
    touch config.py
    random_key=$(openssl rand -base64 32)
    echo "SECRET_KEY = '$random_key'" > config.py
fi