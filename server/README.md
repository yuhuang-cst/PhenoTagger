# run phenobert locally
```shell
cd PhenoTagger
export PYTHONPATH=`pwd`/src:$PYTHONPATH
pip install -r requirements.txt
cd PhenoTagger/src
python ../server/py_pre_download.py
python PhenoTagger_tagging.py -i ../example/input/ -o ../example/output/
```

# Test server locally
Server: 

```shell
export PYTHONPATH=`pwd`/src:`pwd`/server:$PYTHONPATH
pip install -r server/requirements.txt
cd src
python3 ../server/server/service.py
```

Client: 

```shell
cd server
python3 server/test_service.py
```

# Build server image
```shell
mv PhenoTagger/server/ . # Take out the server in advance
cd server # Go to dir where Dockerfile is located

# Build image (since docker can only contain things in the current directory, temporarily move other code packages in and out)
mv ../PhenoTagger .
docker build --network=host -t phenotagger:v20230722 ./
mv ./PhenoTagger ../

# Try to run container
docker container run --rm -p 8086:8086 phenotagger:v20230722
python server/test_service.py # In anather terminal

# Put server back
cd .. && mv server PhenoTagger
```

## debug in container
```shell
# Run container in the background：
docker run -itd --entrypoint /bin/bash -p 8086:8086 --name phenotagger phenotagger:v20230722
# Go into the container
docker exec -it phenotagger bash
```

# Image export and import
```shell
# Export image tar
docker save [imageID] -o ./phenotagger.tar

# Import image tar
docker load -i phenotagger.tar
docker tag [imageID] phenotagger:v20230722 # re-tag
```

# Running service
```shell
docker container run --rm -d -p 8086:8086 phenotagger:v20230722
```
