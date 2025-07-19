#/bin.bash

mkdir ./config
mkdir ./data_summary

python -m venv kanban-temp
source ./kanban/bin/activate
pip install -r requirements.py
rm -r ./kanban-temp

python3 generate_config.py