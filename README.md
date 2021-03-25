# SynCreator

## Local Installation
```
# clone the repository
$ git clone https://github.com/rcastley/SynCreator
$ cd SynCreator
$ python3 -m venv venv
$ . venv/bin/activate
# On a Raspberry Pi run pip3 install wheel
$ pip3 install -e .
$ export FLASK_APP=flaskr
$ flask init-db
$ nohup waitress-serve --call 'flaskr:create_app' > log.txt 2>&1 &
```
Open http://localhost:8080 in a browser to use the SynCreator app to simulate conditions. You will need to initially register a username & password.

To use the API test functionality click on **API** on menu bar to get your unique URL e.g. http://localhost:8080/api/v1/{username}/books/all. You can run both GET & POST test types. The POST test requires a JSON payload containing `{"title":"Read a book"}` to the endpoint http://localhost:8080/api/v1/{username}/books. You can GET individual ID's my using http://localhost:8080/api/v1/*{username}*/books?id=0. ID's 0-2 are supported, anything else will 404.

**NEW:** Support for Control Groups - https://help.rigor.com/hc/en-us/articles/115004817328-How-to-Create-an-Event-Annotation-. In the UI, under Control Groups dropdown, enter Control Group ID and post token. When you change condition an Event Annotation will fire and be visible on the scatter plot.

The `venv` environment will persist at rest until you delete the venv file.

## Installation on AWS Free Tier

- Create a new Ubuntu 20.04 instance
  - AMI link: aws-marketplace/ubuntu/images/hvm-ssd/ubuntu-focal-20.04-amd64-server-20210129-aced0818-eef1-427a-9e04-8ba38bada306 
  - Use the t2.micro instance within the AWS "free tier"
  - When configuring the Security Group, add a rule to allow port 8080 on the TCP protocol
  - Finally, choose an existing key pair, you will use this key to connect via SSH
  - It takes a few minutes for AWS to provision the host
  - Note the IP address you are given and use below in <insertyourip>
  - Then at a terminal (answer y when prompted):

``` 
$ ssh ubuntu@<insertyourip>
$ sudo apt update
$ sudo apt-get install python3-venv
$ git clone https://github.com/rcastley/SynCreator
$ cd SynCreator
$ python3 -m venv venv
$ . venv/bin/activate
$ pip3 install -e .
$ export FLASK_APP=flaskr
$ flask init-db
$ nohup waitress-serve --call 'flaskr:create_app' > log.txt 2>&1 &
```
Open `http://\<insertyourip\>:8080` in a browser.

The `venv` environment will persist at rest until you delete the venv file.
