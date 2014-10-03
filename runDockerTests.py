#docker requires sudo, so if using virtualenv, run with e.g.
#sudo venv/bin/python runDockerTests.py

import io
import tarfile
import os
import json

import docker

client = docker.Client(base_url='unix://var/run/docker.sock', 
                        #version='1.12',
                        timeout=10)

container = client.create_container("longtest",
                "nosetests --with-json --json-file='tests/testMore.json' tests/testMore.py")
                #nosetests needs full path to output file in this situation, default gives error (why?)
                #"nosetests tests/testMore.py")
                #"python3 tests/testMore.py")

client.start(container)

#for log in client.logs(container, stdout=True, stderr=True, stream=True):
#    print(log)



#now collect test results
#various options:
#using docker data volume feature (?)
#push files out to somewhere
#leave them in containers and fish them out afterwards


print(client.wait(container)) #wait for tests to finish

#http://stackoverflow.com/questions/22683410/docker-python-client-api-copy
def copy_from_docker(client, container_id, src, dest):
    reply = client.copy(container_id, src)
    filelike = io.BytesIO(reply.read())
    tar = tarfile.open(fileobj = filelike)
    file = tar.extractfile(os.path.basename(src))
    with open(dest, 'wb') as f:
        f.write(file.read())

copy_from_docker(client, container, "/tests/testMore.json", "result.json")

results = None

with open ("result.json") as file:
    results = json.load(file)

for result in results['results']:
    print(result['time'])




