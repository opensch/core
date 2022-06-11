import os

# Automatically create config.py from env

def replaceSettings(config, name, data):
	config = config.replace("self."+name+' = ""', name+' = "'+data+'"')
	return config

with open("config.py.sample") as f:
	config = f.read()

environ = os.environ
for i in environ.keys():
	config = replaceSettings(config, i, environ[i])

with open("config.py", "w") as f:
        f.write(config)
