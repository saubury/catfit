# Introduction

_Snowy’s eating — tweeting my cats weight & dining habits with a Raspberry Pi_

Our cat Snowy 😸 has been enjoying her meals over winter. I wanted to start collecting data on her eating habits, and analyse her weight over time. This data is collected with food and cat weight measurements; alongside phots taken by two cameras. Data is collected and images processed locally using a Raspberry Pi.


![Diagram indicting two scales and camera placement](./docs/overview.png "Diagram indicting two scales and camera placement
")


# Setup
- Clone this repo

## Python and Pip setup
- Ensure Python 3, virtualenv and pip are installed.
```
which python3

virtualenv -p `which python3` venv
source venv/bin/activate
python --version
pip --version
pip install -r requirements.txt 
```

## Submodule Setup
```
git submodule add https://github.com/tatobari/hx711py
```

```
 git submodule update --init --recursive
 ```
 

## Service Setup
```
sudo cp catfit.service /lib/systemd/system
sudo systemctl daemon-reload
sudo systemctl enable catfit.service
sudo systemctl start catfit.service
```

# General checks
General checks for determining what's going on with the service.
```
sudo systemctl status catfit.service
sudo journalctl -u catfit.service -b
sudo journalctl -u catfit.service -b -f
ps -ef | grep catfit | grep -v grep
```


