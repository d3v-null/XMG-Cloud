# XMG-Cloud
Google Cloud App Engine interface for [Xero Map Generator](https://github.com/derwentx/Xero-Map-Generator)

Largely based off [this tutorial](https://cloud.google.com/python/getting-started/tutorial-app)

# Setup

See: [Setting Up a Python Development Environment](https://cloud.google.com/python/setup)

If you use pyenv, you can use pyenv-virtualenv to create your virtual Python3 environment.

```bash
pyenv virtualenv 3 xmg-cloud
pyenv activate xmg-cloud
pip install -r requirements.txt -r requirements-dev.txt
```

# Configuration

This app is designed to take part of its configuration from environment
variables, so that it can easily be run on multiple environments. To switch
between environments locally, you can create multiple `app.*.yaml` files
containing environment variables. Make sure not to commit these files to a
public repository!

You will need to create a project in Google Cloud Console for each environment
you wish to set up (`your-production-project-id` / `your-staging-project-id`).

For each project you will need to perform several steps:

## Create the environment app config file

```bash
echo 'env_variables:' >> app.[ENVIRONMENT].yaml
```

## Create an App Engine application and enable billing in that project
[Go To App Engine](https://console.cloud.google.com/projectselector/appengine/create?lang=flex_python&st=true&_ga=2.209047506.-1904653949.1530240882)

Set the `GOOGLE_CLOUD_PROJECT` environment variable to your staging project id in your CI settings and your environment app config file.
```bash
echo $'- GOOGLE_CLOUD_PROJECT: \'[YOUR-STAGING-PROJECT-ID]\'' >> app.[ENVIRONMENT].yaml
```

## Enable the Cloud Datastore, Cloud Pub/Sub, Cloud Storage JSON and Stackdriver Logging APIs.
[Enable the APIs](https://console.cloud.google.com/flows/enableapi?apiid=datastore.googleapis.com,datastore,pubsub,storage_api,logging,plus,sqladmin.googleapis.com&redirect=https://console.cloud.google.com&_ga=2.204779344.-1904653949.1530240882)

## Create a Cloud Storage bucket
see [Using Cloud Storage with Python](https://cloud.google.com/python/getting-started/using-cloud-storage)
```bash
gsutil mb gs://[YOUR-BUCKET-NAME]
gsutil defacl set public-read gs://[YOUR-BUCKET-NAME]
```

set the `CLOUD_STORAGE_BUCKET` environment variable to your staging bucket name in your CI settings and your environment app config file.

```bash
echo $'- CLOUD_STORAGE_BUCKET=\'[YOUR-STAGING-BUCKET-NAME]\'' >> app.[ENVIRONMENT].yaml
```

## Create a Web Application Client ID

See [Authenticating Users with Python](https://cloud.google.com/python/getting-started/authenticate-users)

set the `GOOGLE_OAUTH2_CLIENT_ID` and `GOOGLE_OAUTH2_CLIENT_SECRET` environment
variables in your CI settings and your environment app config file.

```bash
echo $'- GOOGLE_OAUTH2_CLIENT_ID=\'[YOUR-CLIENT-ID]\'' >> app.[ENVIRONMENT].yaml
echo $'- GOOGLE_OAUTH2_CLIENT_SECRET=\'[YOUR-CLIENT-SECRET]\'' >> app.[ENVIRONMENT].yaml
```

# Testing

source the local environment variables that were set in the staging environment app config

```bash
pip install shyaml
cat app.staging.yaml | shyaml key-values-0 env_variables | xargs -0 -n2 -J{} sh -c 'echo export $1=$2' -- {} > .staging.env
source .staging.env
```

Run local unit tests with

```bash
py.test
```

Lint and test on all supported python versions with

```bash
tox
```

Run the webserver locally
```bash
python main.py
```

Configure your Travis environment

# Deploying to an App Engine Environment
```
gcloud app deploy --project [YOUR-ENVIRONMENT-PROJECT-ID] app.yaml app.[ENVIRONMENT].yaml
```
## Production
```
gcloud app deploy --project [YOUR-PRODUCTION-PROJECT-ID] app.yaml app.production.yaml
```
