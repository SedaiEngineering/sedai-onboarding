#! /bin/bash

if ! command -v kubectl  &> /dev/null
then
    echo "kubectl could not be found"
    exit
fi

LABEL="sedai-kube-topology-reader"

red="\033[1;31m"
green="\033[1;32m"

curl https://raw.githubusercontent.com/SedaiEngineering/sedai-onboarding/main/tools/sedai-kubernetes-topology-collector.yaml -o sedai-kubernetes-topology-collector.yaml

echo -e "\e[1;32mLaunching Collector!"$rescolor""
kubectl apply -f sedai-kubernetes-topology-collector.yaml
sleep 90

status=$(kubectl get pods --selector="app=$LABEL" | grep $LABEL | awk '{print $3}')
    if [[ ! $status =~ ^Running$|^Completed$  ]]  ; then
        echo -e "\e[1;31mError !"$rescolor""
        exit
    else
        echo -e "\e[1;32mOK!"$rescolor""
        kubectl cp sedai-kube-topology-reader-59d7989f9f-jdhj7:/home/sedai/topology.json topology.json 
        echo " "
        echo "Starting Cleanup"
        kubectl delete -f sedai-kubernetes-topology-collector.yaml
        echo "Cleanup Complete"
        echo "Please send the topology.json Sedai Team"
    fi