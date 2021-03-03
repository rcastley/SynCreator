# SynCreator

## Local Installation
```
# clone the repository
$ git clone https://github.com/rcastley/SynCreator
$ cd SynCreator
$ python3 -m venv venv
# On a Raspberry Pi run pip3 install wheel
$ . venv/bin/activatepip3
$ pip3 install -e .
$ export FLASK_APP=flaskr
$ export FLASK_ENV=development
$ flask init-db
$ nohup flask run -h 0.0.0.0 -p 8080 > log.txt 2>&1 &
```
Open http://localhost:8080 in a browser to use the SynCreator app to simulate conditions.

To stop the app press `ctrl+c` in your terminal to quit or just close the terminal.

The `venv` environment will persist at rest until you delete the venv file.

## Installation on AWS Free Tier
```
- Create a new Ubuntu 20.04 instance
  - AMI link: aws-marketplace/ubuntu/images/hvm-ssd/ubuntu-focal-20.04-amd64-server-20210129-aced0818-eef1-427a-9e04-8ba38bada306 
  - Use the t2.micro instance within the AWS "free tier"
  - When configuring the Security Group, add a rule to allow port 8080 on the TCP protocol
  - Finally, choose an existing key pair, you will use this key to connect via SSH
  - It takes a few minutes for AWS to provision the host
  - Note the IP address you are given and use below in <insertyourip>
  - Then at a terminal (answer y when prompted):
 
$ ssh ubuntu@<insertyourip>
$ sudo apt update
$ sudo apt-get install python3-venv
$ git clone https://github.com/rcastley/SynCreator
$ cd SynCreator
$ python3 -m venv venv
$ . venv/bin/activate
$ pip3 install -e .
$ export FLASK_APP=flaskr
$ export FLASK_ENV=development
$ flask init-db
$ nohup flask run -h 0.0.0.0 -p 8080 > log.txt 2>&1 &
```
Open `http://\<insertyourip\>:8080` in a browser.

To stop the app press `ctrl-c` in your terminal to quit or just close the terminal.

The `venv` environment will persist at rest until you delete the venv file.
