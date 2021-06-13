
Ensure Python 3, virtualenv and pip are installed.



```
which python3

virtualenv -p `which python3` venv
source venv/bin/activate
python --version
pip --version
pip install -r requirements.txt 
```

## Submodule

```
https://github.com/tatobari/hx711py
git submodule add https://github.com/tatobari/hx711py
```

```
 git submodule update --init --recursive
 ```
 

## Miscellaneous

Setup

```
sudo cp catfit.service /lib/systemd/system

sudo systemctl daemon-reload
sudo systemctl enable catfit.service
sudo systemctl start catfit.service
```

General checks for determining what's going on with the service.

```
sudo systemctl status catfit.service
sudo journalctl -u catfit.service -b
sudo journalctl -u catfit.service -b -f
ps -ef | grep catfit | grep -v grep
```

## Python

Ensure Python 3, `virtualenv` and `pip` are insatlled.

```
which python3

virtualenv -p `which python3` venv
source venv/bin/activate
python --version
pip --version
pip install -r requirements.txt
```


## Fixes for Raspberry Pi

When running ` pip install -r requirements.txt` got the error `Running setup.py install for confluent-kafka ... error`

https://github.com/edenhill/librdkafka#build-from-source

```
sudo apt remove librdkafka*
```