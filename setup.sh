#!/bin/bash

function run_tools_containers(){
    echo "Building and launching DBeaver and Codeserver only...";
    (docker-compose -f docker-compose.tools.yml up -d --force-recreate --build);
    (docker image ls bravo_ready*);
}

function run_all_containers(){
    echo "Building and launching all containers...";
    (docker-compose -f docker-compose.yml up -d --force-recreate --build);
    (docker image ls bravo_ready*);
}

function update_tags(){
    echo "Updating tags...";
    (docker image ls bravo_ready*);
    (docker images | awk '$1 ~ /^bravo_ready/ { print $1 }' | xargs -I {} docker tag {}:latest {}:bravo);
    (docker image ls bravo_ready*:latest | awk '{print $1}' | xargs -I {} docker rmi {}:latest);
    (docker image ls *:bravo);
}

function make_tar(){
    echo "Building tar...";
    (docker save -o bravostack.tar $(docker image ls bravo_ready*));
}

function load_tar(){
    echo "Loading tar...";
    (docker load -i bravostack.tar);
}

function remove_docker_cache(){
    echo 'Showing reclaimable memory...';
    (docker system df);
    echo "Removing docker cache...";
    (docker system prune -a -f);
}

echo "What would you like to do?"
select pd in "Run tools containers" "Run all containers" "Update tags" "Make tar" "Load tar" "Remove docker cache" "Quit"; do
    case $pd in
        "Run tools containers" ) run_tools_containers; break;;
        "Run all containers" ) run_all_containers; break;;
        "Update tags" ) update_tags; break;;
        "Make tar" ) make_tar; break;;
        "Load tar" ) load_tar; break;;
        "Remove docker cache" ) remove_docker_cache; break;;
        "Quit" ) exit;;
        * ) echo "Invalid option";;
    esac
done
