from angr/angr:latest

user angr
workdir /home/angr
run /home/angr/.virtualenvs/angr/bin/pip install stopit
copy download.sh /home/angr
copy process.py /home/angr
#entrypoint [ "/home/angr/download.sh" ]
