import os
import base64
import subprocess

# Automatically create config.py from env

def replaceSettings(config, name, data):
	config = config.replace("self."+name+' = ""', "self."+name+' = "'+data+'"')
	return config

with open("config.py.sample") as f:
	config = f.read()

environ = os.environ
for i in environ.keys():
	config = replaceSettings(config, i, environ[i])

with open("config.py", "w") as f:
        f.write(config)

# Add SSL support for nginx

if 'SSL' in os.environ and os.environ['SSL'] == "1":
	sslCert = base64.b64decode(os.environ['SSL_CERT']).decode()
	sslKey = base64.b64decode(os.environ['SSL_KEY']).decode()

	with open("/etc/nginx/ssl_cert.pem", "w") as f:
		f.write(sslCert)
	with open("/etc/nginx/ssl_key.pem", "w") as f:
		f.write(sslKey)

	os.remove("/etc/nginx/nginx.conf")
	os.rename("/etc/nginx/nginx.conf.ssl", "/etc/nginx/nginx.conf")
	subprocess.call(["nginx", "-s", "reload"])
