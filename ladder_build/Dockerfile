FROM python:3.7.9

COPY . .

RUN python3.7 setup.py build_ext --inplace
RUN mv mapanalyzerext.*.so mapanalyzerext.so

CMD ["/bin/bash"]
