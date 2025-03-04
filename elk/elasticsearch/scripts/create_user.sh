#!/bin/bash

# Variables
ELASTICSEARCH_HOST="http://localhost:9200"
KIBANA_USER="kibana_user"
KIBANA_PASSWORD="kibana_password"

curl -X POST "localhost:9200/_security/user/kibana_user" -H "Content-Type: application/json" -u elastic:elastic_password -d'
{
  "password" : "kibana_password",
  "roles" : [ "kibana_system" ],
  "full_name" : "Kibana User",
  "email" : "kibana_user@example.com"
}



# # Authenticate Kibana user
# response=$(curl -s -o /dev/null -w "%{http_code}" -u $KIBANA_USER:$KIBANA_PASSWORD $ELASTICSEARCH_HOST)

# if [ $response -eq 200 ]; then
#     echo "Authentication successful"
# else
#     echo "Authentication failed with status code: $response"
# fi



'