Create a simple API server in any lang you want which interacts with docker registry:2 
running on your machine
You may pack a docker registry and API server inside docker-compose to easier test. 
The API server should have the route `/history?name=<image_name>&tag=<image_tag>`
When a user requests this URL the history of docker image layers responded with lines used in Dockerfile to build the image
* please don't use any docker interaction libraries
* hashes instead of filenames are allowed
* Docker registry can be run on localhost to simplify interaction with it by using HTTP instead of https
