## Getting Started with development

### Environment

- clone canary

```bash
git clone https://github.com/PodcastIO/canary.git
```

- create virtual env, Python 3.9.9+ required

```
cd canary/server
python3 -m venv .venv
```

- install requirements

```
pip install  -r requirements.txt --no-dependencies
```

- add PYTHONPATH

```
export PYTHONPATH=canary/server/src:${PYTHONPATH}
```

### launch server

- launch server

```bash
python main.py server
```

- launch scheduler

```
python main.py scheduler
```

- launch other job executor

```
python main.py rq --name=other
```

- launch tts job executor

```
python main.py rq --name=en
```

### VSCode Settings

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "server",
      "type": "python",
      "request": "launch",
      "program": "${workspaceFolder}/src/podcast/main.py",
      "args": ["server"],
      "env": {
        "PYTHONPATH": "${workspaceFolder}/src${env:PYTHONPATH}"
      }
    },
    {
      "name": "scheduler",
      "type": "python",
      "request": "launch",
      "program": "${workspaceFolder}/src/podcast/main.py",
      "args": ["scheduler"],
      "env": {
        "PYTHONPATH": "${workspaceFolder}/src${env:PYTHONPATH}"
      }
    },
    {
      "name": "other",
      "type": "python",
      "request": "launch",
      "program": "${workspaceFolder}/src/podcast/main.py",
      "args": ["rq", "--name=other"],
      "env": {
        "PYTHONPATH": "${workspaceFolder}/src${env:PYTHONPATH}"
      }
    },
    {
      "name": "zh",
      "type": "python",
      "request": "launch",
      "program": "${workspaceFolder}/src/podcast/main.py",
      "args": ["rq", "--name=zh"],
      "env": {
        "PYTHONPATH": "${workspaceFolder}/src${env:PYTHONPATH}"
      }
    },
    {
      "name": "en",
      "type": "python",
      "request": "launch",
      "program": "${workspaceFolder}/src/podcast/main.py",
      "args": ["rq", "--name=en"],
      "env": {
        "PYTHONPATH": "${workspaceFolder}/src${env:PYTHONPATH}"
      }
    }
  ]
}
```
