---
title: Seamless Streaming Backend/Frontend
emoji: 📞
colorFrom: blue
colorTo: yellow
sdk: docker
pinned: false
suggested_hardware: t4-medium
---

# Seamless Streaming demo
## Running on HF spaces
You can simply duplicate the space to run it.

## Running locally
### Install backend seamless_server dependencies

`cd seamless-experiences/seamless_vc/seamless_server`

If running for the first time, create conda environment:
```
conda create --name smlss_server python=3.8
conda activate smlss_server
pip install -r requirements.txt
```

### Install frontend streaming-react-app dependencies
```
conda install -c conda-forge nodejs
cd streaming-react-app
npm install
npm run build  # this will create the dist/ folder
```


### Running the server

The server can be run locally with uvicorn below.
Run the server in dev mode:

```
uvicorn app_pubsub:app --reload --host localhost
```

Run the server in prod mode:

```
uvicorn app_pubsub:app --host 0.0.0.0
```

To enable additional logging from uvicorn pass `--log-level debug` or `--log-level trace`.


### Debuging

If you enable "Server Debug Flag" when starting streaming from the client, this enables extensive debug logging and it saves audio files in /debug folder. 