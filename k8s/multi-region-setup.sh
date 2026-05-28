#!/bin/bash

# Deploy to multiple regions
REGIONS=("us-east-1" "eu-west-1" "ap-southeast-1")

for region in "${REGIONS[@]}"; do
    echo "Deploying to $region..."
    
    # Create cluster
    gke-deploy create-cluster foresight-$region --region $region
    
    # Deploy services
    helm install foresight ./helm/foresight -n foresight
    
    # Configure DNS failover
    gcloud dns record-sets update foresight.ai \
        --rrdatas=foresight-$region.example.com \
        --ttl=60
done

echo "Multi-region deployment complete!"
