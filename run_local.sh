#!/bin/bash

SERVER_PORT=${1-5000}
export SERVER_PORT=${SERVER_PORT}
export DATABASE_HOST=localhost
export DATABASE_PORT=5432
export DATABASE_USER=dhos-users-api
export DATABASE_PASSWORD=dhos-users-api
export DATABASE_NAME=dhos-users-api
export AUTH0_DOMAIN=https://login-sandbox.sensynehealth.com/
export AUTH0_AUDIENCE=https://dev.sensynehealth.com/
export AUTH0_METADATA=https://gdm.sensynehealth.com/metadata
export AUTH0_JWKS_URL=https://login-sandbox.sensynehealth.com/.well-known/jwks.json
export AUTH0_MGMT_CLIENT_ID=someid
export AUTH0_MGMT_CLIENT_SECRET=secret
export AUTH0_AUTHZ_CLIENT_ID=someid
export AUTH0_AUTHZ_CLIENT_SECRET=secret
export AUTH0_AUTHZ_WEBTASK_URL=https://draysonhealth-sandbox.eu.webtask.io/someid/api
export AUTH0_CLIENT_ID=someid
export AUTH0_CUSTOM_DOMAIN=dev
export AUTH0_HS_KEY=secret
export NONCUSTOM_AUTH0_DOMAIN=https://draysonhealth-sandbox.eu.auth0.com
export ENVIRONMENT=DEVELOPMENT
export ALLOW_DROP_DATA=true
export PROXY_URL=http://localhost
export HS_KEY=secret
export FLASK_APP=dhos_users_api/autoapp.py
export IGNORE_JWT_VALIDATION=true
export REDIS_INSTALLED=False
export LOG_FORMAT=colour
export CUSTOMER_CODE=DEV
export TOKEN_URL=https://draysonhealth-sandbox.eu.auth0.com/oauth/token
export DISABLE_CREATE_USER_IN_AUTH0=True
export RABBITMQ_DISABLED=true
         

if [ -z "$*" ]
then
   flask db upgrade
   python -m dhos_users_api
else
flask $*
fi
