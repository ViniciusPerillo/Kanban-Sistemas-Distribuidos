#/bin.bash

mkdir ./config
mkdir ./data_summary

cd ./data_summary/
touch stock_data.txt
chmod a+rwx stock_data.txt
touch factory_data.txt
chmod a+rwx factory_data.txt
touch product_data.txt
chmod a+rwx product_data.txt
cd ..

python3 -m venv kanban-temp
source ./kanban-temp/bin/activate
pip install -r requirements.txt
python3 generate_config.py
rm -r ./kanban-temp