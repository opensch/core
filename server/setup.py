from flask import Response

def setup(request):
    args = [
        'MONGO_HOST',
        'MONGO_PORT',
        'MONGO_USER',
        'MONGO_PASS',
        'MONGO_DB_PREFIX',
        'adminUser',
        'adminPass'
        'clientID',
        'clientSecret'
    ]

    optionalArgs = [
        'port',
        'ssl_context',
        'googleFCM'
    ]

    argsLeft = request.form.copy()
    for i in args:
        if i not in request.form:
            return Response("Missing argument: " + i, status = 400)
        argsLeft.pop(i)
    
    for i in argsLeft.keys():
        if i not in optionalArgs:
            return Response("Unknown argument: " + i, status = 400)

    wasPort = False

    if len(request.form['clientSecret']) < 16:
        return Response("clientSecret must be at least 16 characters long", status = 400)
    if len(request.form['adminPass']) < 8:
        return Response("adminPass must be at least 8 characters long", status = 400)

    fileContents = "class Config():\n\tdef __init__(self):\n"
    for i in request.form.keys():
        if i == "port":
            wasPort = True
        if i == "MONGO_PORT" or i == "port":
            fileContents += "\t\tself." + i + " = " + request.form[i] + "\n"
        else:
            fileContents += "\t\tself." + i + " = '" + request.form[i] + "'\n"
    fileContents += "\t\tself.mode = 'production'\n"

    if wasPort == False:
        fileContents += "\t\tself.port = 8900\n"
    
    with open("config.py", "w") as f:
        f.write(fileContents)
    
    return Response("Config saved! Restart the instance to apply the changes", status = 200)

def setupDummy(request, school):
    return Response("This instance is already setup. You can change the settings by manually editing config.py.", status = 200)