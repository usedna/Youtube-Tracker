#!/bin/bash

check_success() {
    if [ $? -ne 0 ]; then
        echo "$1"
        exit 1
    else
        echo "$2"
    fi
}


switch_docker(){    
    if [ "${1,,}" == "disable" ] ; then
        action="disable"
    else
        action="enable"
    fi

    err_service_msg="Error: Failed to ${action} docker sevice."
    scc_service_msg="Docker Service was ${action}d successfully"

    if systemctl is-active --quiet docker ; then
        if [ $action == "enable" ] ; then
            echo "Docker Service is active"
        else
            echo "Docker Service is enabled. Proceed to disable the service..."
            sudo systemctl stop --now docker docker.socket
        fi
    else
        if [ $action == "enable" ] ; then
            echo "Docker Service is disabled. Proceed to enable the service..."
            sudo systemctl enable --now docker
        else
            echo "Docker Service is inactive"
        fi
    fi

    check_success "$err_service_msg" "$scc_service_msg"
}


compose(){
    err_compose_msg="Error: Failed to create and run containers"
    scc_compose_msg="Containers were created successfully"

    docker compose up -d
    check_success "$err_compose_msg" "$scc_compose_msg"
}


case $1 in

    "disable")
        switch_docker $1
        ;;
    "compose")
        compose
        ;;
    *)
        switch_docker
        compose
        ;;
esac