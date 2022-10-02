#! /bin/bash

source venv/bin/activate
export PYTHONPATH=${PYTHONPATH}:/usr/src/app/src
export QTWEBENGINE_DISABLE_SANDBOX=1  # ebook-convert run as root
exec python src/podcast/main.py ${@}