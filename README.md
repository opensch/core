openSchool Core is the reference implementation of the openSchool server, written in Python. It's meant for running on school server infrastructure to provide openSchool functionality to the students / workers of the faculty. It is designed for running from something small like a Raspberry Pi to more complex structures, security and privacy.

:warning: **A word of causion!** This software is in its early stages of development and in no way considered production-ready. Expect a lot of bugs and quite poor design decisions in place that will (hopefully) get cleared up over time. There will be pull requests that **wlll** break current functionality.

# Installation
There are several ways to get your hands on Core:

## Docker Container
We provide a pre-configured Linux environment in the form of a Docker Image. That way you can run isolated instances of openSchool Core on your server.

To setup:
  1. Clone the Docker image by typing in the prompt: `docker pull opensch/core`
  
  2. Download the configuration script: [config.py](https://raw.githubusercontent.com/opensch/core/master/config.py.sample), and set it up.
  
  3. To run a container, run: `docker run -v <PATH TO YOUR CONFIG FILE>:/app/config.py -p 80:80 opensch/core`

## Kubernetes
In case you need to run Core on a big scale, we have setup a Kubernetes configuration file for fast deployments

To setup:
  1. Download the Kubernetes .yaml file: [apply_openSchool.yaml](https://raw.githubusercontent.com/opensch/core/master/apply_openSchool.yaml)
  
  2. Configure the amount of replicas and the environment parameters.
  
  3. To start the cluster, run: `kubectl apply -f apply_openSchool.yaml`

## Manually
To run openSchool Core you will need:
  * A Linux based environment
  * python 3 (3.6 and higher is recommended)
  * pymongo
  * flask
  * An HTTP server (if running in production)

We recommend this configuration, as it has been thorougly tested:
  * Arch Linux with the default Linux Kernel Package
  * Nginx
  * MongoDB running on a separate server

Note that Core can be run on other operating systems **in development mode**. However, they are **not** oficially supported for running in production.

To setup:
  1. Clone the Core repository. Download the ZIP or type in the terminal:
```
git clone https://github.com/opensch/core.git
```
  
  2. Install the dependencies by running:
```
pip install -r requirements.txt
```
  
  3. Rename `config.py.example` to `config.py`, open and fill up the blank variables.
  
  4. In the configuration script (`config.py`) set the `self.mode` variable to "production" if running on the server or "development" if running locally. The development option also disable security measures and checks.
  
  5. Configure your web server to run the FastCGI application, if you are in the production environment. Otherwise, you can use the Flask built-in web server.
  In that case, run:
  ```
  sudo python main.py
  ```

# Contributions
Any contributions to the source code, documentation edits and feature proposals are welcome. If you also want to support the projects, you can also send a donation. The ways of reaching out to us are in the README of the GitHub organization.

# License
This software is distributed under the Server Side Public License Version 1

For more information check the [LICENSE file](https://github.com/opensch/core/blob/master/LICENSE).