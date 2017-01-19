#!/bin/bash

mysql -u root<<EOFMYSQL
DROP DATABASE flaskcard;
CREATE DATABASE flaskcard;
EOFMYSQL
