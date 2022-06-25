ENV=$1

if [ $ENV == 'DEV' ]; then
    export PORT="8000"
    export IP="127.0.0.1"
    export FILENAME="logs/dev.log"
    export DATABASE_URL="instances/dev-sql.db"
    uvicorn app:app --reload --port $PORT --host $IP
elif [ $ENV == 'PROD' ]; then
    export PORT="80"
    export IP="0.0.0.0"
    export FILENAME="logs/prod.log"
    export DATABASE_URL="instances/prod-sql.db"
    uvicorn app:app --reload --port $PORT --host $IP --workers 10
fi

