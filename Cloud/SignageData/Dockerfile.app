FROM ubuntu-signage_data:latest
COPY . /signage_data
WORKDIR /signage_data
RUN pip3 install -r requirements.txt
RUN pip3 install -e .
RUN ./install.sh
ENTRYPOINT ["./run.sh"]
