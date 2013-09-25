mv votainteligente.db vi_backup.db
python manage.py syncdb --noinput
python manage.py migrate
python manage.py loaddata example_data.yaml