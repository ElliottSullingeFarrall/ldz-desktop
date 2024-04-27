clear

start_server() {
    echo "Starting server..."
    (uwsgi --plugin python3 --http :4000 --home .venv --wsgi-file wsgi.py &> wsgi.log &)
    read PID < <(pgrep -f "uwsgi --plugin python3 --http :4000 --home .venv --wsgi-file wsgi.py")
    echo "Server started with PID $PID"
}
restart_server() {
    echo "Restarting server..."
    kill -9 $PID &> /dev/null
    sleep 3
    (uwsgi --plugin python3 --http :4000 --home .venv --wsgi-file wsgi.py &> wsgi.log &)
    read PID < <(pgrep -f "uwsgi --plugin python3 --http :4000 --home .venv --wsgi-file wsgi.py")
    echo "Server started with PID $PID"
}
stop_server() {
    echo "Stopping server..."
    kill -9 $PID &> /dev/null
    sleep 3
    echo "Server stopped"
}

start_server
trap stop_server EXIT
while inotifywait -q -r -e modify --exclude '__pycache__' src; do
   restart_server
done
