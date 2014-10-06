#docker requires sudo, so if using virtualenv, run with e.g.
#sudo venv/bin/python runDockerTests.py

"""
Farm out unit tests to Docker containers and collect the results.
Some assumptions:
    * the container base image has a straight copy of all the local tests
    * all tests are in a single test directory (no support for recursion here)
    * tests all succeed (not examining test results or restarting containers on failure)
    * containers exit cleanly
"""


import io
import tarfile
import os
import json
import inspect
import time

import docker
import nose

start_time = time.time()

client = docker.Client(base_url='unix://var/run/docker.sock')
JSON_RESULTS_FILENAME = "result.json"
TESTS_DIRECTORY = "tests"
IMAGE_NAME = "longtest"
JSON_RESULTS_PATH = os.path.join(TESTS_DIRECTORY, JSON_RESULTS_FILENAME)

#Use nosetests to find paths to individual tests
test_paths = []
nose_test = nose.loader.TestLoader()
for test_file in nose_test.loadTestsFromDir(TESTS_DIRECTORY):
    for test_case in test_file:
        for test in test_case:
            address = test.address()
            test_filename = os.path.relpath(address[0])
            test_name = address[2]
    
            test_paths.append("%s:%s" % (test_filename, test_name))


#Build a container to run each individual test
containers = []
for test_path in test_paths:
    command = "nosetests --with-json --json-file='%s' %s" % (JSON_RESULTS_PATH, test_path)
    container = client.create_container(IMAGE_NAME, command)
    containers.append(container)


#Start containers
print("Starting %d containers" % len(containers))
for container in containers:
    client.start(container)

#Wait for all containers to exit
for container in containers:
    client.wait(container)

def collect_results(client, containers):
    """Fish out and aggregate JSON test results from all containers"""
    results = []
    for container in containers:
        reply = client.copy(container, "%s" % JSON_RESULTS_PATH)
        filelike = io.BytesIO(reply.read())
        tar = tarfile.open(fileobj = filelike)
        result_file = tar.extractfile(os.path.basename(JSON_RESULTS_FILENAME))
        for line in result_file:
            #is it safe to assume ascii here?
            #print(json.loads(line.decode("ascii")))
            results.extend(json.loads(line.decode("ascii"))['results'])
    return results

#Collect aggregated test results
results = collect_results(client, containers)

#Clean up containers
for container in containers:
    client.remove_container(container)

#Have a look
print([result['time'] for result in results])

print("--- %s seconds ---" % (time.time() - start_time))
