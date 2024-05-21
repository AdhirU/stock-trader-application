# Instructions on how to run the code

- Create a Python3.8 Virtual Environment
- Run `pip install -r requirements.txt` in the root folder to install the required libraries for the project
- Run `docker compose up --build` in the root folder to build the containers for each service
- Note the IP Address for the frontend service, and run `python client.py <ip> <p>` where `ip` is the frontend ip address and `p` is the probability of trade

# Installing the application in AWS EC2

- sftp the Docker files and src folder to EC2 instance
- Download and install python3.8 and python3.8-venv
- Create Python3.8 virtual environment
- Run `pip install -r requirements.txt`
- Install Docker and create Docker group. Add Port 8080 to the open ports for the instance
- Run `docker compose up --build`
- Note the public IP address in the `instance.json` file
- Run `python client.py <ip> <p>` where `ip` is the public IP address of the EC2 instance and `p` is the probability of trade.