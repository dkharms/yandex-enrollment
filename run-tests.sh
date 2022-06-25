export FILENAME="logs/test.log"
export DATABASE_URL="instances/test-sql.db"
python -m pytest app/test -s -v
