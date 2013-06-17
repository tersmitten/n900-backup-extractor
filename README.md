# N900 backup extractor

Backup extraction scripts for the Nokia N900 (Maemo 5).

## Dependencies

### osso-abook-export.py

```
sudo apt-get install libdb-dev
export BERKELEYDB_DIR=/usr/include/
```

```
pip install bsddb3
pip install vobject
pip install slugify
```

### rtcom-eventlogger-export.py

```
sudo apt-get install libsqlite3-dev
```

```
pip install pysqlite
```

## Usage

### osso-abook-export.py ([see](http://blog.tersmitten.nl/how-to-export-your-contacts-from-a-n900-backup-directory.html))

```
python osso-abook-export.py <path to addressbook.db>
```

### rtcom-eventlogger-export.py ([see](http://blog.tersmitten.nl/how-to-export-your-text-messages-from-a-n900-backup-directory.html))

```
python rtcom-eventlogger-export.py <path to el-v1.db> <path to csv file>
```
