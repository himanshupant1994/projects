# Introduction


## Steps to setup docker in ubuntu20.04 on Windows Machine:

- Install ubuntu20.04 from Microsoft store
- Open command prompt and type `ubuntu2004` & It will take sometime to install OS
- Type your username and password and follow below commands
```
sudo su root
sudo apt-get update
sudo apt-get upgrade
docker
sudo apt-get install apt-transport-https ca-certificates curl software-properties-common
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
sudo apt-get update
sudo apt-get install docker-ce 
Enable "Expose daemon on tcp://localhost:2375 without TLS" from Docker Desktop
docker -H localhost:2375 images
docker -H localhost:2375 run hello-world
echo "export DOCKER_HOST=localhost:2375" >> .bashrc
source .bashrc
sudo apt install python3-pip
```


### Reference:
https://medium.com/@sebagomez/installing-the-docker-client-on-ubuntus-windows-subsystem-for-linux-612b392a44c4
