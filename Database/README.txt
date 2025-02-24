Currently, the database hosted via docker container works through LAN connections w/ TCP protocol.
This folder contains everything to initialize the docker containers and insert the database with the data
Backend for interacting with database is currently WIP.

docker-compose.yml
    # This is the file that creates the necessary docker containers including the mariaDB container.
    To run: 
        docker-compose up -d

    Recommended: interface w/ Docker GUI

/data
    # This is the static data to be entered into the database upon intializing the database through docker-compose.
    # Script is WIP for automating the updating/inserting of data entries 

    To access the mariaDB database
        Ensure docker container is running:
            # Lists running docker containers
            docker ps
            # If not running, start the container
            docker start ufid_database
        
        Access through mysql:
            mysql -h 127.0.0.1 -P 3306 --protocol=TCP -u myuser -p

        Access directly through docker:
            docker exec -it ufid_mariadb mariadb -u myuser -p

        Password = mypass

    To insert entries into the mariaDB database (MariaDB):
        SHOW DATABASES; # Shows available databases within MariaDB 
        USE ufid_database; # Switches usage to ufid_database
        Copy + paste sql entries from /data folder
            This creates 2 tables within the ufid_database, each with multiple entries: courses, exams
            roster.sql WIP
        SHOW TABLES; # courses and exams should be shown

WIP
    1. Refactor backend to interact with the mariaDB database hosted on docker
    2. Set up docker/database on a server that can be remotely accessed safely anywhere instead of utilizing LAN connections

