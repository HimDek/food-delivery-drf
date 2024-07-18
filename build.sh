python3.12 -m venv venv
source venv/bin/activate

pip install -r requirements.txt
rm -rf ./venv/lib/python3.12/site-packages/googleapiclient/discovery_cache/documents/
pip uninstall pip -y
du -h -d 1 ./venv/lib/python3.12/site-packages | sort -h
mkdir staticfiles_build