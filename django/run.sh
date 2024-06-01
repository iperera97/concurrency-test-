#!/bin/bash

pipenv shell

gunicorn -b 0.0.0.0:80 --workers=3 --threads=3 main.wsgi