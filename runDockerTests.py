#docker requires sudo, so if using virtualenv, run with e.g.
#sudo venv/bin/python runDockerTests.py

"""
Farm out unit tests to Docker containers and collect the results.
Some assumptions:
    * the container base image has a straight copy of all the local tests
    * all tests are in a single test directory (no support for recursion here)
    * tests all succeed (not examining test results or restarting containers on failure)
"""


import io
import tarfile
import os
import json
import inspect

import docker
import nose

client = docker.Client(base_url='unix://var/run/docker.sock')
JSON_RESULTS_FILENAME = "result.json"
TESTS_DIRECTORY = "tests"
IMAGE_NAME = "longtest"
JSON_RESULTS_PATH = os.path.join(TESTS_DIRECTORY, JSON_RESULTS_FILENAME)

#Use nosetests to find files containing tests
test_files = []
nose_test = nose.loader.TestLoader()
for test_suite in nose_test.loadTestsFromDir(TESTS_DIRECTORY):
    test_filename = inspect.getfile(test_suite.context)
    test_files.append(os.path.relpath(test_filename))

#Build a container to run each test file
containers = []
for test_file in test_files:
    command = "nosetests --with-json --json-file='%s' %s" % (JSON_RESULTS_PATH, test_file)
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
            print(json.loads(line.decode("ascii")))
            results.extend(json.loads(line.decode("ascii"))['results'])
    return results

#Collect aggregated test results
results = collect_results(client, containers)

#Have a look
print([result['time'] for result in results])

