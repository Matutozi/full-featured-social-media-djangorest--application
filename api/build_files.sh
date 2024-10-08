# build_files.sh

pip install -r requirements.txt
python3.9 manage.py collectstatic --no-input --clear

python3.9 manage.py makemigrations --verbosity=3
python3.9 manage.py migrate