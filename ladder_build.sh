docker build . -f ./ladder_build/Dockerfile -t maextbuild
id=$(docker create maextbuild)
docker cp $id:./mapanalyzerext.so ./MapAnalyzer/cext/mapanalyzerext.so
docker rm -v $id

