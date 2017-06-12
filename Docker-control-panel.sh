#!/bin/bash
# docker command menu with ncurses
# need docker and dialog packages 
# there is little more functionality to be included.

#functions - start

funcDisplayMenu () {
 dialog --title "Docker Control Panel" --menu "please choose action" 15 45 6 1 "List Docker images" 2 "List Docker containers" 3 "Docker image delete" 4 "Docker container delete" 5 "Docker container run" q "Q for quit" 2>menu_choice.txt
}

funcDisplayMenu2 () {
 dialog --title "$1" --menu "$2" 15 45 "$3" 1 "$4" 2 "$5" 3 "$6" 4 "$7" 5 "$8"
}

funcInputBox () {
 dialog --title "$1" --inputbox "$2" 15 45
}

funcMsgBox () {
 dialog --title "$1" --msgbox "$2" "$3" "$4"
}

funcExit () {
rm -rf input_choice*.txt
rm -rf menu_choice*.txt
echo "Good Bye........"
}

#functions - end

#script -start

trap 'funcExit' SIGINT

#test for docker service for systemd OS

clear
systemctl status docker | grep running

if [ $? -eq "0" ]; then
echo "Docker Service is On proceeding..."
else
systemctl start docker
echo "Docker service has been started"
fi


funcDisplayMenu


case "`cat menu_choice.txt`" in
 1) echo "Listing Images..."
    echo "================="
    docker images
    sleep 5
    exec bash "$0";;

 2) funcDisplayMenu2 "Listing Type" "Choose container listing type" 4 "All Container procesess" "Only active containers" "Stop running container" "restart stoped container" 2>menu_choice5.txt
    case "`cat menu_choice5.txt`" in
    1) echo "Listing all Containers"
       echo "======================"
       docker ps -a
       sleep 5
       exec bash "$0";;
    
    2) echo "Listing Containers"
       echo "=================="
       docker ps
       sleep 5
       exec bash "$0";;
   
    3) funcInputBox "Container Stop" "Which container to stop (name/id)" 2>input_choice7.txt
       docker stop "`cat input_choice7.txt`"
       sleep 2
       exec bash "$0";;

    4) funcInputBox "Container Restart" "Which container to restart (menu/id)" 2>input_choice8.txt
       docker restart "`cat input_choice8.txt`"
       sleep 2
       exec bash "$0";;
    esac;;

 3) echo "Choose an image to delete..."
    funcInputBox "Delete Image" "Please type image to delete" "10" "20" 2>input_choice.txt
    funcMsgBox "IMAGE DELETION" "You are now deleting image from Docker please choose OK" "10" "20"
    docker rmi "`cat input_choice.txt`"
    sleep 2
    exec bash "$0";;

 4) echo "Choose container to remove.."
    funcInputBox "Remove container" "Type container to remove" 2>input_choice.txt
    funcMsgBox "CONTAINER DELETION" "You are now deleting the container please choose OK" "10" "20"
    docker rm "`cat input_choice.txt`"
    sleep 2
    exec bash "$0";;

 5) echo "Creating container..."
    funcDisplayMenu2 "Container Options" "Please choose container type" 2 "Interactive Container" "Detached Container" 2>menu_choice2.txt
    case "`cat menu_choice2.txt`" in
    1) VAR1="-it"
       echo "$VAR1";;
    2) VAR1="-itd"
       echo "$VAR1";;
    esac

    funcDisplayMenu2 "Container Volume Options" "Please choose attached Volume" 2 "Container with attached Volume" "Container without attached Volume" 2>menu_choice3.txt
    case "`cat menu_choice3.txt`" in
    1) funcInputBox "Container Volume" "Please type the volume and where to attach it" 2>input_choice2.txt
       VAR2="-v `cat input_choice2.txt`";;

    2) echo "You have chosen no volume for the container";;
    esac
    
    funcDisplayMenu2 "Container Port Options" "Please choose port redirection" 2 "With port redirect" "Without port redirect" 2>menu_choice4.txt
    case "`cat menu_choice4.txt`" in
    1) funcInputBox "Container Ports" "Please container and host port separate them with ":" " 2>input_choice3.txt
       VAR3="-p `cat input_choice3.txt`";;

    2) echo "There will be no port redirection";;
    esac

    funcInputBox "Starting command" "Please type for command to start the container with (blank for none)" 2>input_choice4.txt
    VAR4="`cat input_choice4.txt`"

    funcInputBox "Image selection" "Please type image to use for the container" 2>input_choice5.txt
    VAR5="`cat input_choice5.txt`"

    funcInputBox "Container Name" "Please type the container name" 2>input_choice6.txt
    VAR6="--name `cat input_choice6.txt`"

    DOCKER="docker run $VAR1 $VAR2 $VAR3 $VAR6 $VAR5 $VAR4"
    $DOCKER
    sleep 5
    exec bash "$0";;

 q) echo "We are now quiting.."
    funcExit;;
esac
