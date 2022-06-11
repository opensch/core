# This is openSchool core

Welcome to the repository of openSchool Core - the reference implementation of the openSchool server designed for running on local servers. Here you will find everything you'll need for running openSchool on your server setups. 

**Serious warning:** openSchool is a very new project. And it is **extremely** buggy and in no way can be called production-ready. So keep that in mind when you decide to run this software in a production environment.

# Wait, what is openSchool?
openSchool is a set of free and open tools for managing, automating and combining various routines of school and university management. Our goal is to create a central hub for storing student/employee data, managing timetables and marks and so forth.

# Installation

## Docker
  1. `docker pull opensch/core`
  2. Download [config.py](https://raw.githubusercontent.com/opensch/core/master/config.py.sample) from this repository and setup it.
  3. `docker run -v <PATH TO YOUR CONFIG FILE>:/app/config.py -p 80:80 opensch/core`

## Manually
To run openSchool Core, you will need:
* Python 3 (just in case make sure to have version 3.6 and higher)
* Pymongo
* Flask
* A HTTP web server

The recommended setup that was thoroughly tested by the staff is:
* Arch Linux with the default Linux Kernel
* Nginx as the web server

Note that openSchool Core can be run under Windows or macOS, but only in development mode with the built-in Flask web server. Otherwise these operating systems are **unadvised** and **not supported officially**.

# Installation steps:
1) Clone the repository from GitHub via Zip download or by typing:
```
git clone https://github.com/opensch/backend.git
```

2) Install the required dependencies by running:
```
pip install -r requirements.txt
```

3) Rename ```config.py.sample``` to ```config.py```. Open the file and fill the blank variables with needed values.

4) In the configuration file set the variable ```self.mode``` to ```production``` if you are running on a real server. Don't forget to fill ```self.clientID``` and ```self.clientSecret```. If you are doing development work, set the mode to ```development```. In that case you can ignore the above mentioned variables.

5) Configure your webserver to execute the FastCGI application. If you are using Nginx, as adviced, you can use the default configuration, which is stored in the repository. For development purposes, you can just run:
```
sudo python main.py
```

# Documentation
We are working on creating and translating the documentation for the openSchool Core. It is not done yet, so please wait.

# Can I take openSchool for a spin without configuring the server?
Currently, no. As the project is very new, no school is running any instances of openSchool. So for the time being you need to setup your own server to test out openSchool.

# [License](https://github.com/opensch/backend/blob/main/LICENSE)
