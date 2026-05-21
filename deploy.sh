#!/bin/bash
CONTENT=$(base64 < index-responsive.html | tr -d '\n')
SHA=$(openssl sha256 -sha256 < index-responsive.html | awk '{print $2}')

curl -s -X POST "https://api.vercel.com/v13/deployments" \
  -H "Authorization: Bearer $1" \
  -H "Content-Type: application/json" \
  -d "{
    \"name\": \"metodo-francotirador-888\",
    \"files\": [{
      \"file\": \"index-responsive.html\",
      \"data\": \"$CONTENT\",
      \"digest\": \"$SHA\"
    }],
    \"projectSettings\": {
      \"outputDirectory\": \".\"
    }
  }"
