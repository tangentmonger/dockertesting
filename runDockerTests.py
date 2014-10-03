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
container2 = client.create_container("longtest",
                "nosetests --with-json --json-file='tests/testLong.json' tests/testLong.py")
                #nosetests needs full path to output file in this situation, default gives error (why?)

client.start(container)
client.start(container2)

#now collect test results
#various options:
#using docker data volume feature (?)
#push files out to somewhere
#leave them in containers and fish them out afterwards

print(client.wait(container2)) #this one takes longer
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
copy_from_docker(client, container2, "/tests/testLong.json", "result2.json")

results = None
results2 = None

with open ("result.json") as file:
    results = json.load(file)

with open ("result2.json") as file:
    results2 = json.load(file)

mergedResults = results['results']
mergedResults.extend(results2['results'])

for result in mergedResults:
    print(result['time'])




