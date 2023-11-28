# Seamless Streaming Server

## Setting up the AWS server

- Clone working AMI with things set up: https://us-west-2.console.aws.amazon.com/ec2/home?region=us-west-2#ImageDetails:imageId=ami-013fc3fb27faa03e5
- This has the conda environment, repository, model etc set up so minimal install was required

- Open port tunnelling via ssh so you can connect to the AWS server via localhost (gets around some security issues): e.g. `ssh -L 8000:localhost:8000 -L 3000:localhost:3000 -L 5173:localhost:5173 -i ~/.ssh/mduppes_devserver.pem  ec2-user@44.231.140.195`

## Setting up the dev environment

Clone the repo

`cd seamless-experiences/seamless_vc/seamless_server`

If running for the first time, create conda environment from the environment.yaml `conda env create -f environment.yml`
(or if you are on Mac OS, replace `environment.yml` with `environment_mac.yml`)

In each new terminal you use you will need to activate the conda environment:
`conda activate smlss_server`

Install dependencies with pip:
`pip install -r requirements.txt`

Install Meta-specific dependencies with the dedicated install script:
`./scripts/update_meta_dependencies.sh`

If needed, download and extract the latest model using the dedicated script:
`./scripts/download_latest_models.sh`

## Setting up the docker environment

Alternatively we can build a docker image (for ease of deployment).

1. Make sure github keys are loaded into ssh-agent. Copy over the keys into ~/.ssh/ then run `eval $(ssh-agent)`, then `ssh-add` to load the keys.
2. Run `docker-compose build` if you just want to build the image. If you want to also run the server: `docker compose up --build`.
3. Optionally to push the built docker image to ECR so it could be pulled into deployments: `./deploy.sh` 

NOTE: Add your models to the ./models directory.

# Running the v2 ("pubsub") server

The pubsub server can be loaded with docker above or run locally with uvicorn below.
Run the server in dev mode:

```
uvicorn app_pubsub:app --reload
```

Run the server in prod mode:

```
uvicorn app_pubsub:app --host 0.0.0.0
```

To enable additional logging from uvicorn pass `--log-level debug` or `--log-level trace`.

## Running the frontend

- For the v2 pubsub server, the frontend lives in the streaming-react-app root directory (not seamless_ui).

## Updating the conda environment after changes to environment.yml

Run this command to install/remove packages to match the current environment.yml file:

`conda env update --prefix ./env --file environment.yml  --prune`

See: https://conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html?highlight=sharing#updating-an-environment

## Debuging

If you enable "Server Debug Flag" when starting streaming from the client, this enables extensive debug logging and it saves audio files in /debug folder. test_no_silence.wav contains data with silence chunks removed.
