#!/bin/bash

# (docker load --input="python_app.tar");
# (docker images);
# (docker tag 77814a09fe71 python_app);

# (docker load --input="postgres_db.tar" );

# (docker images);

# (docker commit 0d8330b3b305 brv_python_app && docker save brv_python_app > brv_python_app.tar);
# (docker commit c5dc905d5ffc brv_postgres_db && docker save brv_postgres_db > brv_postgres_db.tar);

# (docker save -o bravoStack.tar $(docker image ls *:bravo));
# (docker load -i bravoStack.tar);