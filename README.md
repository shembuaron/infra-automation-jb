# Infra-Automation

**LINUX ONLY**

Python script to automate provisioning of EC2 machines and service installations

*Note: The script currently only mocks the provisioning process and saves the configuration files locally.*

![infra-automation screenshot](https://files.catbox.moe/48taph.png)

## How to run:

### With uv (recommended):

Install [uv](https://docs.astral.sh/uv/) and then:
```bash
git clone https://github.com/shembuaron/infra-automation-jb.git
cd infra-automation-jb/
uv run python main.py
```


### With pip
```bash
git clone https://github.com/shembuaron/infra-automation-jb.git
cd infra-automation-jb/
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python main.py
```


*This project is licensed under the DWUWWI-1.0 (Do Whatever You Want With It) license*
