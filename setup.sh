#!/bin/bash

function run_tools_containers(){
    echo "Building and launching DBeaver and Codeserver only...";
    (docker-compose -f docker-compose.tools.yml up -d --force-recreate --build);
    (docker image ls bravoopana*);
}

function run_all_containers(){
    echo "Building and launching all containers...";
    (docker-compose -f docker-compose.yml up -d --force-recreate --build);
    (docker image ls bravoopana*);
}

function update_reponames(){
    echo "Updating repo names...";
    # Get a list of Docker images and iterate through them
    for image in $(docker images | awk '{print $1}' | grep "bravoopana-")
    do
    # Get the current image tag without the prepended name and underscore
    tag=$(echo $image | sed 's/bravoopana-//')

    # Tag the image with the new tag
    docker tag $image $tag

    # Remove the old image with the prepended name and underscore
    docker rmi $image
    done;
}

function update_tags(){
    echo "Updating tags...";
    (docker image ls bravo*);
    (docker images | awk '$1 ~ /^bravo/ { print $1 }' | xargs -I {} docker tag {}:latest {}:bravo);
    (docker image ls bravo*:latest | awk '{print $1}' | xargs -I {} docker rmi {}:latest);
    (docker image ls *:bravo);
}

function make_tar(){
    echo "Building tar...";
    (docker images | awk '$1 ~ /^bravo/ { print $1 }' | xargs -I {} docker save -o {}.tar {});
   #(docker save -o bravostack.tar $(docker image ls *:bravo));
}

function load_tar(){
    echo "Loading tars...";
    (docker images | awk '$1 ~ /^bravo/ { print $1 }' | xargs -I {} docker load -i {}.tar);
    # (docker load -i bravostack.tar);
}

function remove_docker_cache(){
    echo 'Showing reclaimable memory...';
    (docker system df);
    echo "Removing docker cache...";
    (docker system prune -a -f);
}

echo "What would you like to do?"
select pd in "Run tools containers" "Run all containers" "Update Repo Names" "Update tags" "Make tar" "Load tar" "Remove docker cache" "Quit"; do
    case $pd in
        "Run tools containers" ) run_tools_containers; break;;
        "Run all containers" ) run_all_containers; break;;
        "Update Repo Names" ) update_reponames; break;;
        "Update tags" ) update_tags; break;;
        "Make tar" ) make_tar; break;;
        "Load tar" ) load_tar; break;;
        "Remove docker cache" ) remove_docker_cache; break;;
        "Quit" ) exit;;
        * ) echo "Invalid option";;
    esac
done
