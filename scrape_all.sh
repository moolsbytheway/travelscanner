sh ./cleanup.sh

DIRECTORY="./src"

for file in "$DIRECTORY"/___*.py
do
    echo "Webscraping $file..."
    [ -f "$file" ] && ./venv/bin/python3 "$file"
done