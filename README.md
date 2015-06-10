# yamato-inventory

Script to migrate yamato inventory.

## How to install dependencies

Ensure you have python 2.6+ installed.
Install python libs with following commands.

```
$ wget https://bootstrap.pypa.io/ez_setup.py
$ python ez_setup.py
$ easy_install pip

$ pip install pymysql
$ pip install requests
$ pip install openpyxl
$ pip install pyyaml
```

NOTE: You might need to `sudo` each command for permissions.

## How to run script to migrate data.

```
$ python yamato_excel.py <path to excel file>
```

## How to run script to generate csv files.

```
$ python csv_exporter.py
```

## How to run script to sync stock to PCMS.
```
$ python pcms_stock.py
```
