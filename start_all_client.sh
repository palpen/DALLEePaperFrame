# Script that starts all the clients

# Path to repository in each raspberry pi
PATH_TO_REPO=/home/pi/DALLEePaperFrame
SERVER_IP_ADDR="10.0.0.87"

# Host names
declare -a arr=(
#    "raspberrypi0.local"
#    "raspberrypi1.local"
    "raspberrypi2.local"
    "raspberrypi3.local"
#    "raspberrypi4.local"
    "10.0.0.67"
)

# Command to run inside a screen session
main_cmd="
    cd $PATH_TO_REPO/client && \
    bash $PATH_TO_REPO/client/run_client.sh $SERVER_IP_ADDR $PATH_TO_REPO/config.yml
"

# Command that starts a screen session in detached mode and runs $main_cmd
screen_cmd="screen -dmS running_client bash -c \"$main_cmd\""

for host in "${arr[@]}"
    do
       echo "Running client in $host..."
        # SSH into client, start a screen session,
        # start the client, then exit the ssh session"
        ssh pi@$host "screen -XS running_client quit; $screen_cmd"
    done
wait
