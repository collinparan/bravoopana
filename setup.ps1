function run_tools_containers(){
    Write-Output "Building and launching DBeaver and Codeserver only...";
    (docker-compose -f docker-compose.tools.yml up -d --force-recreate --build);
    (docker image ls bravo_ready*);
}

function run_all_containers(){
    Write-Output "Building and launching all containers...";
    (docker-compose -f docker-compose.yml up -d --force-recreate --build);
    (docker image ls bravo_ready*);
}

function update_tags(){
    Write-Output "Updating tags...";
    (docker image ls bravo_ready*);
    (docker images | Select-String -Pattern '^bravo_ready' | ForEach-Object { docker tag $_.ToString():latest $_.ToString():bravo });
    (docker image ls bravo_ready*:latest | Select-String '{print $1}' | ForEach-Object { docker rmi $_.ToString():latest });
    (docker image ls *:bravo);
}

function make_tar(){
    Write-Output "Building tar...";
    (docker save -o bravoStack.tar $(docker image ls *:bravo));
}

function load_tar(){
    Write-Output "Loading tar...";
    (docker load -i bravoStack.tar);
}

function remove_docker_cache(){
    Write-Output 'Showing reclaimable memory...';
    (docker system df);
    Write-Output "Removing docker cache...";
    (docker system prune -a -f);
}

Write-Output "What would you like to do?"
$choices = "Run tools containers", "Run all containers", "Update tags", "Make tar", "Load tar", "Remove docker cache", "Quit"
$defaultChoice = $choices[0]
$cancelChoice = "Quit"

do {
    $index = 1
    foreach ($choice in $choices) {
        Write-Output "$index. $choice"
        $index++
    }
    $selected = Read-Host "Please select an option"
} until ($choices.Contains($selected))

switch ($selected) {
    "Run tools containers" { run_tools_containers }
    "Run all containers" { run_all_containers }
    "Update tags" { update_tags }
    "Make tar" { make_tar }
    "Load tar" { load_tar }
    "Remove docker cache" { remove_docker_cache }
    "Quit" { exit }
    default { Write-Output "Invalid option" }
}
