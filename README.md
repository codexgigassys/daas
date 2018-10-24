# DaaS
## What is DaaS?
"Decompilation-as-a-Service" or "DaaS" is a tool designed to change the way of file decompiling. An analyst usually decompile malware samples one by one using a program with a GUI. That's pretty good when dealing with a few samples, but it becomes really tedious to do with larger amounts. Not to mention if you have to decompile different types of files, with different tools and even different operating systems. Besides, that cannot be integrated with other programs because the decompilers use a GUI. DaaS aims to solve all those problems at the same time. The most external layer of DaaS is docker-compose, so it can run on any OS with docker support. All the other components run inside docker so now we can integrate the decompiler with any program on the same computer. In addition, we developed an API to use DaaS from the outside, so you can also connect the decompiler with programs from other computers and use the decompiler remotely.

Although the tool's modular architecture allows you to easily create workers for decompiling many different file types, we started with the most challenging problem: decompile .NET executables. To accomplish that, we used Wine on a Docker container to run Windows decompailers flawlessly on a linux environment. In addition, on Windows some programs create useless or invisible windows in order to work, so we needed to add xvfb (x11 virtual frame buffer; a false x11 environment) to wrap those decompilers and avoid crashes on our pure command line environment. This allows you to install DaaS in any machine without desktop environment and be able to use any decompiler anyway.


## Summarized features
- Automatized malware decompilation.
- Use decompilers designed for Windwos or Linux on any operative system.
- Code designed in an extensible and comprehensible way, so everyone can add new decompilers.
- Support for lots of samples submited at the same time, thanks to asynchronous responses and a queue system.
- Support for binaries and libraries to be used as decompilers.
- Decompilers that create windows work flawlessly on a CLI enviroment.
- Keep all decompilation results together in one place and download them whenever you want.
- Advanced statistics about decompiled samples.


## How to install
Requirements:
Install [docker](https://docs.docker.com/install/) and [docker-compose](https://docs.docker.com/compose/) on any operative system.

```
mkdir daas && cd daas
git clone https://github.com/codexgigassys/daas
cd daas
```
Now you are on the folder with docker-compose.yml file. You can start DaaS whenenever you want using:
```
sudo docker-compose up -d
```

In case you want to stop DaaS and start it again later, use the following commands:
```
sudo docker-compose stop
sudo docker-compose start
```

## Increase Security

DaaS is an open source software, so some passwords and keys used here can be seen by everyone. It's recommended to change them manually.
This changes are not necessary for DaaS to work, so you can skip this section if you want.

### Django configuration

Go to /daas/settings.py, and look for the following lines:
```
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '9v8%0qt7p4y$)*%(%5(hr9cyp_v2=fevxl6dg7jt$!#q3dh5s4'
```
And change the SECRET_KEY value. [Click here](https://docs.djangoproject.com/en/2.1/ref/settings/#std:setting-SECRET_KEY) for more information.

```
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
```
Set DEBUG = False.

### Database Password

Go to /daas/settings.py, and look for the following lines:
```
# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'daas',
        'USER': 'daas',
        'PASSWORD': 'iamaweakpassword',
        'HOST': 'db',
        'PORT': '5432',
    }
}
```
Change 'iamaweakpassword' for any password you want.

Then look for docker-compose-yml on the root directory of DaaS, and replace the password there too:
```
  db:
    image: postgres:10.5
    ports:
      - "5432:5432"
    volumes:
      - ../postgres-data:/var/lib/postgresql/data
    environment:
      POSTGRES_USER: daas
      POSTGRES_PASSWORD: iamaweakpassword
      POSTGRES_DB: daas
    links:
      - syslog
    logging:
      driver: syslog
      options:
        syslog-address: "udp://127.0.0.1:5514"
        tag: "db"
```


## Adding new compilers
This may change for better in future releases. We aim to make this process as easy as possible.

### 1. Dockerization
First, we need to create a docker image for the decompiler.
For that purpose, create a copy of peWorkerDockerfile on DaaS root directory and rename it. This will be your decompiler's docker file.
It will look like this:
./yourDecompilerWorkerDockerfile:
```
FROM python:3.7.0-stretch
RUN mkdir /daas
WORKDIR /daas
ADD . /daas
ENV PYTHONUNBUFFERED=0
ENV HOME /home/root


# Generic
RUN apt-get clean && \
apt-get update && \
apt-get install --no-install-recommends -y build-essential apt-transport-https && \
apt install --assume-yes gnutls-bin \
unzip \
xauth \
zenity \
xvfb \
host
```

Here you will need to know how to create a docker file. It's recommended to just let that generic stuff as is, and add your changes below.
For instance, in the flash decompiler we added some lines to install the decompiler:
```
FROM python:3.7.0-stretch
# ...


# Added for flash decompiler:
ADD ./utils/jre /jre


# Generic
RUN apt-get clean && \
# ...


# Added for flash decompiler:
RUN apt-get install -y swftools && \
apt-get update && \
apt-get install -y java-common libxxf86vm1 libxtst6 libgl1 libasound2 && \
dpkg -i /jre/oracle-java8-jre_8u161_amd64.deb && \
rm -f -v /jre/oracle-java8-jre_8u161_amd64.deb && \
echo "c3aa860aa04935a50a98acb076819deb24773e5cc299db20612e8ef037825827  /tmp/ffdec.deb" > /tmp/ffdec.sha256 && \
wget -nv --no-check-certificate https://www.free-decompiler.com/flash/download/ffdec_10.0.0.deb -O /tmp/ffdec.deb && \
sha256sum -c /tmp/ffdec.sha256 && \
dpkg -i /tmp/ffdec.deb && \
rm -f /tmp/ffdec.deb && \
rm -f /tmp/ffdec.sha256
```
Other decompilers are easy to install, however. This will depend on what decompiler you want to use.

If you can import the decompiler as a python library, then installing it will be reduced to only add the following line at the end of your docker file:
```
RUN pip install <your decompiler's package name>
```

Then you need to go to docker-compose.yml:
./docker-compose.yml
```
version: '2'
services:
  api:
    # ...

  redis:
    # ...

  db:
    # ...

  pe_worker:
    # ...

  flash_worker:
    build:
      context: .
      dockerfile: flashWorkerDockerfile
    command: bash -c "sleep 15 && pip --retries 10 install -r /daas/pip_requirements_worker.txt && rq worker --path /daas/daas/daas_app --url redis://daas_redis_1:6379/0 flash_queue --name agent_$$(hostname -I | cut -d' ' -f1)_$$(echo $$RANDOM)__$$(date +%s)"
    volumes:
      - .:/daas
    tmpfs:
      - /tmpfs
    links:
      - syslog
    depends_on:
      - api
      - redis
      - syslog
    mem_limit: 3g
    memswap_limit: 3g
    mem_reservation: 1g
    logging:
      driver: syslog
      options:
        syslog-address: "udp://127.0.0.1:5514"
        tag: "flash_worker"

  syslog:
    # ...
```

We commented everything on the above example except the part related to flash decompiler.

To add your own decompiler, you will need to add another section on docker-compose.yml.
Here is a template:
```
  your_decompiler_worker:
    build:
      context: .
      dockerfile: yourDecompilerWorkerDockerfile # this should match the name of the docker file you recently created.
    # In the following line replace "file_type_queue" by "apk_queue" for instance, if you are creating an apk plugin.
    command: bash -c "sleep 15 && pip --retries 10 install -r /daas/pip_requirements_worker.txt && rq worker --path /daas/daas/daas_app --url redis://daas_redis_1:6379/0 file_type_queue --name agent_$$(hostname -I | cut -d' ' -f1)_$$(echo $$RANDOM)__$$(date +%s)"
    volumes:
      - .:/daas
    tmpfs:
      - /tmpfs
    links:
      - syslog
    depends_on:
      - api
      - redis
      - syslog
    mem_limit: 3g
    memswap_limit: 3g
    mem_reservation: 1g
    logging:
      driver: syslog
      options:
        syslog-address: "udp://127.0.0.1:5514"
        tag: "file_type_worker" # Change this too. You are able to use any tag, for instance: "apk_worker".
```
You only need to change "dockerfile", "command" and "tag". However, if you like to customize it more, you are able to.

At this point, the hardest part is already finished.

### 2. Select what samples to send
#### 2.1 Create a filter
Now you need a filter, to choose what samples will be sent to your decompiler:
./daas/daas_app/decompilers/filters.py:
```
from .filter_utils import mime_type, pe_mime_types, flash_mime_types


def pe_filter(data):
    return mime_type(data) in pe_mime_types


def flash_filter(data):
    return mime_type(data) in flash_mime_types
    
# ...
```

This function receives the sample binary data and returns a boolean to say whether it should be sent to the processor we are creating or not.
The mime type is usually fine, so you can use an already defined filter if there is one.

#### 2.2 Run the decompiler
Here you should add basic information about the decompiler and how to run it.
If your decompiler is installed on your system as a package or requires wine, follow the instructions of 2.2A
If you use a python library, read the instructions of 2.2B instead

#### 2.2A Binary decompiler
Look for:
./daas/daas_app/decompilers/decompiler.py:
```
class YourFileTypeWorker(SubprocessBasedWorker): # change it!
    def set_attributes(self):
        self.an_attribute = value  # use this format to set values to attributes if necessary.
                                   # look below to a full list of all attributes
```

| Attribute  | Type | Description | Default | Required to change |
| ------------- | ------------- | ------------- | ------------- | ------------- |
| nice_value | Integer | Priority of the process (see linux nice command). Zero is the default priority. | 0 | No |
| timeout_value | Integer | Timeout in seconds. Use zero or a negative number to disable timeout. | 120 | No |
| name | String | File type. For example: "apk" | "You should change name on subclasses!" | Yes |
| decompiler_command | List of Strings | A list with an string for every part of a bash command to run the decompiler. In example: ["echo" "hello world!"]. | - | Yes |
| decompiler_name | String | Decompiler's name. | "Name of the program used to decompile on this worker!" | Yes |
| custom_current_working_directory | String | The current working directory used by python subprocess library | Decompilation directory | No |

#### 2.2B Library decompiler
Look for:
./daas/daas_app/decompilers/decompiler.py:
```
class YourFileTypeWorker(LibraryBasedWorker): # change it!
    def decompile(self):
        """ Should be overriden by subclasses.
        This should return output messages (if there are some), or '' if there isn't anything to return. """
```
Follow the instructions of "decompile" method and override it.
When you need access to the sample or set a directory to decompile, use the following methods respectively: 
- get_tmpfs_folder_path()
- get_tmpfs_file_path()


#### 2.3 Add a relation among the filter, the queue and the worker.
Now you have a worker listening on the task queue. However, nothing will be sent there yet.
In order to send files there, you need to go to:
./daas/daas_app/decompilers/utils.py:
```
# ...

class RelationRepository(Singleton):
    def __init__(self):
        self.relations = [Relation(pe_filter, "pe_queue", "pe_redis_worker"),
                          Relation(flash_filter, "flash_queue", "flash_redis_worker"),
                          Relation(file_type_filter, "file_type_queue", "file_type_redis_worker"] # add an item!

# ...
```
There:
file_type_filter: The name of the function you created (or selected from the default ones) in the previous steep (2.1), without quotes!
file_type_queue: The same value used in docker-compose.yml
file_type_redis_worker: The name of the function you created (or selected from the default ones) in the steep 2.2, with quotes!


#### 2.4 Add the worker
TODO


## DaaS architecture
![Daas Architecture](https://github.com/codexgigassys/daas/blob/master/daas_architecture.jpeg)


## Licence Notice
This file is part of "Decompiler as a Service" (also called DaaS).

DaaS is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

DaaS is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with DaaS.  If not, see https://www.gnu.org/licenses/gpl-3.0.en.html.

For the files and folders in the "/utils/just_decompile" folder, see the licence present on that folder. There are also links to the source code if you are interested.
