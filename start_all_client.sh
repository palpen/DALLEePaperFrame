# Script that starts all clients passed in as arguments
# Usage: ./start_all_client.sh user@host1 user@host2 user@host3

# Path to repository in each raspberry pi
PATH_TO_REPO=/home/pi/DALLEePaperFrame
SERVER_IP_ADDR="10.0.0.87"

# Command to run inside a screen session
main_cmd="
    cd $PATH_TO_REPO/client && \
    bash $PATH_TO_REPO/client/run_client.sh $SERVER_IP_ADDR $PATH_TO_REPO/config.yml ||
    exec bash
"

# Command that starts a screen session in detached mode and runs $main_cmd
screen_cmd="screen -dmS running_client bash -c \"$main_cmd\""

for client in "$@"
    do
       echo "Running client in $client..."
        # SSH into client, start a screen session,
        # start the client, then exit the ssh session"
        ssh $client "screen -XS running_client quit; $screen_cmd" &
    done
wait
