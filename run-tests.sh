export FILENAME="logs/test.log"
export DATABASE_URL="sqlite:///instances/test-sql.db"
python -m pytest app/test -s -v
