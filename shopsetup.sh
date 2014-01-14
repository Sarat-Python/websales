sh syncdb.sh shopadmin root

rm users/migrations/00*

python manage.py schemamigration users --initial

python manage.py migrate users


