Store the dump in a file, transfer the file to the target machine, and then
load the file into the database there. For example, you can dump a database 
to a compressed file on the source machine like this:

shell> mysqldump --quick db_name | gzip > db_name.gz

Transfer the file containing the database contents to the target machine and 
run these commands there:

shell> mysqladmin create db_name
shell> gunzip < db_name.gz | mysql db_name

