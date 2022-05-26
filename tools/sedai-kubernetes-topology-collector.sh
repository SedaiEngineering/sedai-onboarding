#! /bin/bash

if ! command -v kubectl  &> /dev/null
then
    echo "kubectl could not be found"
    exit
fi


LABEL="sedai-kube-topology-reader"

red="\033[1;31m"
green="\033[1;32m"

# Fectch Deployment Configuration.
curl https://raw.githubusercontent.com/SedaiEngineering/sedai-onboarding/main/tools/sedai-kubernetes-topology-collector.yaml -o sedai-kubernetes-topology-collector.yaml

# Run collector Job.
echo -e "\e[1;32mLaunching Collector!"$rescolor""
kubectl apply -f sedai-kubernetes-topology-collector.yaml
sleep 30

# Verify and pull topology.json file.
topologypod=$(kubectl get pods --selector="app=$LABEL" | grep "$LABEL" | awk '{print $1}')
status=$(kubectl get pods --selector="app=$LABEL" | grep "$LABEL" | awk '{print $3}')
    if [[ ! "$status" =~ ^Running$|^Completed$  ]]  ; then
        echo -e "\e[1;31mError !"$rescolor""
        exit
    else
        echo -e "\e[1;32mOK!"$rescolor""
        kubectl cp "$topologypod":/home/sedai/topology.json topology.json 
        echo " "
        echo "Starting Cleanup"
        kubectl delete -f sedai-kubernetes-topology-collector.yaml
        echo "Cleanup Complete"
        echo "Please send the topology.json to Sedai Team"
    fi