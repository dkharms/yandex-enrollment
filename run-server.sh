export ENV=$1
export DATABASE_URL="sqlite:///sql_app.db"

if [ $ENV == 'DEV' ]; then
    export PORT="8000"
    export IP="127.0.0.1"
    export DATABASE_URL="sqlite:///./sql.db"
    uvicorn app:app --reload --port $PORT --host $IP
elif [ $ENV == 'TEST' ]; then
    export PORT="8000"
    export IP="127.0.0.1"
    export DATABASE_URL="sqlite://"
    uvicorn app:app --reload --port $PORT --host $IP
elif [ $ENV == 'PROD' ]; then
    export PORT="80"
    export IP="0.0.0.0"
    export DATABASE_URL="sqlite:///./sql.ab"
    uvicorn app:app --reload --port $PORT --host $IP --workers 10
fi

