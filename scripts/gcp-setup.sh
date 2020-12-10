#!/bin/bash

# Exit if any command fails
set -e

# To avoid hitting gcloud's api quota, we add 1 second delay between commands
shopt -s expand_aliases
alias gcloud_slow='sleep 1 && gcloud'

###################################
# GCP Project: Select or create
###################################
echo -e "\n*** GCP Project: Select or create ***"
GCP_PROJECTS=$(gcloud_slow projects list | awk 'FNR==1 {next} {print $1}')
PS3='Please select your project:'
select GCP_PROJECT in "Create a new project" $GCP_PROJECTS
do
  if [[ ${GCP_PROJECTS[@]} =~ ${GCP_PROJECT} || ${GCP_PROJECT} == "Create a new project" ]]; then
    break
  fi
done

if [[ $REPLY == 1 ]]; then
  echo "Creating a new project, please provide a project name (6 chars min):"
  read;
  GCP_PROJECT=$REPLY
  gcloud_slow config set project $GCP_PROJECT
  gcloud_slow projects create $GCP_PROJECT
fi

gcloud_slow config set project $GCP_PROJECT
echo "Project: $GCP_PROJECT"

###################################
# GCP Region: Select
###################################
echo -e "\n*** GCP Region: Select ***"
GCP_REGIONS=("asia-east1" "europe-west1" "us-central1")
PS3='Please select your region:'
select GCP_REGION in "${GCP_REGIONS[@]}"
do
  if [[ ${GCP_REGIONS[@]} =~ ${GCP_REGION} ]]; then
    break
  fi
done

echo "Region: $GCP_REGION"

###################################
# GCP PubSub: Select telemetry topic 
###################################
echo -e "\n*** GCP Project: PubSub telemetry topic ***"
GCP_TELEMETRY_TOPICS=("Create a new topic" $(gcloud_slow pubsub topics list | awk 'FNR==1 {next} {print $2}' | awk -F'/' '{print $4}'))
PS3='Please select your topic:'
select GCP_TELEMETRY_TOPIC in "${GCP_TELEMETRY_TOPICS[@]}"
do
  echo "$GCP_TELEMETRY_TOPIC"
  if [[ ${GCP_TELEMETRY_TOPICS[@]} =~ ${GCP_TELEMETRY_TOPIC} ]]; then
    break
  fi
done

if [[ $REPLY == 1 ]]; then
  echo "Creating a new topic, please provide a name:"
  read;
  GCP_TELEMETRY_TOPIC=$REPLY
  gcloud_slow pubsub topics create $GCP_TELEMETRY_TOPIC
  echo "Created PubSub telemetry topic: $GCP_TELEMETRY_TOPIC"
fi

#########################################
# GCP IoT Core: Create or select registry
#########################################
echo -e "\n*** GCP IoT Core: Create or select registry ***"
GCP_REGISTRY_NAMES=("Create a new registry" $(gcloud_slow iot registries list --region=$GCP_REGION | awk 'FNR==1 {next} {print $1}'))
PS3='Please select your registry:'
select GCP_REGISTRY_NAME in "${GCP_REGISTRY_NAMES[@]}"
do
  echo "$GCP_REGISTRY_NAME"
  if [[ ${GCP_REGISTRY_NAMES[@]} =~ ${GCP_REGISTRY_NAME} ]]; then
    break
  fi
done

if [[ $REPLY == 1 ]]; then
  echo "Please provide a name for the registry:"
  read;
  GCP_REGISTRY_NAME=$REPLY
  gcloud_slow iot registries create $GCP_REGISTRY_NAME --region $GCP_REGION --event-notification-config=topic=$GCP_TELEMETRY_TOPIC --state-pubsub-topic=$GCP_STATE_TOPIC
  echo "Created IoT Core registry: $GCP_REGISTRY_NAME"
fi


##################################
# GCP IAM: Create key for service account
##################################
echo -e "\n*** GCP IAM: Create key for service account ***"
GCP_SERVICE_ACCOUNT='soundmeter-service-account'

echo -e "\n*** GCP IAM: Get key for service account $GCP_SERVICE_ACCOUNT***"
gcloud_slow iam service-accounts keys create ../data/key.json --iam-account=$GCP_SERVICE_ACCOUNT@$GCP_PROJECT.iam.gserviceaccount.com
echo "Created service account key: key.json"
GCP_ACCOUNT_TOKEN=$(cat data/key.json | tr -s '\n' ' ')

##################################
# Export required variables
##################################

echo -e "\n*** Export env variables ***"
echo "Setup completed, add the following env variables to your target devices:"
echo "GOOGLE_IOT_PROJECT=$GCP_PROJECT"
echo "GOOGLE_IOT_REGION=$GCP_REGION"
echo "GOOGLE_IOT_REGISTRY=$GCP_REGISTRY_NAME"
echo "GOOGLE_IOT_SERVICE_ACCOUNT_TOKEN=$GCP_ACCOUNT_TOKEN"