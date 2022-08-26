# Script that starts all clients passed in as arguments
# Usage: ./start_all_client.sh 1 2 3

# Path to repository in each raspberry pi
PATH_TO_REPO=/home/pi/DALLEePaperFrame
SERVER_IP_ADDR="10.0.0.87"


for client_num in "$@"
    do
        echo "Running client in pi@raspberrypi$client_num.local ..."

        # Command to run inside a screen session
        main_cmd="
            cd $PATH_TO_REPO/client && \
            bash $PATH_TO_REPO/client/run_client.sh $SERVER_IP_ADDR $PATH_TO_REPO/config_rpi$client_num.yml ||
            exec bash
        "

        # Command that starts a screen session in detached mode and runs $main_cmd
        screen_cmd="screen -dmS running_client bash -c \"$main_cmd\""

        # SSH into client, start a screen session,
        # start the client, then exit the ssh session"
        ssh pi@raspberrypi$client_num.local "screen -XS running_client quit; $screen_cmd" &
    done
wait
