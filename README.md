# DaaS
[![Circle CI](https://circleci.com/gh/codexgigassys/daas.png?style=shield)](https://circleci.com/gh/codexgigassys/daas)

# Index
- [What is DaaS?](#what-is-daas)
- [Summarized features](#summarized-features)
- [What is happening behind scenes](#what_is_happening_behind_sceness)
- [Screenshots](#screenshots)
- [About code and releases](#about-code-and-releases)
- [How to install](#how-to-install)
    - [Recomendations](#recomendations)
- [Increase Security](#increase-security)
    - [Django Configuration](#django-configuration)
    - [Database Password](#database-password)
- [Adding new decompilers](#adding-new-decompilers)
    - [Naming conventions](#naming-conventions)
    - [Dockerization](#dockerization)
        - [Docker File](#docker-file)
        - [Docker compose](#docker-compose)
    - [Create a classifier](#create-a-classifier)   
    - [Configure the decompiler](#configure-the-decompiler)
        - [Binary decompiler](#binary-decompiler)
        - [Library decompiler](#library-decompiler)
    - [Optional steps](#optional-steps)
        - [Add an icon for your file type](#add-an-icon-for-your-file-type)
- [DaaS architecture](#daas-architecture)
- [DaaS Thanks](#daas-thanks)
- [Licence Notice](#licence-notice)


# What is DaaS
"Decompilation-as-a-Service" or "DaaS" is a tool designed to change the way of file decompiling. An analyst usually decompiles malware samples one by one using a program with a GUI. That's pretty good when dealing with a few samples, but it becomes really tedious to do with larger amounts. Not to mention if you have to decompile different types of files, with different tools and even different operating systems. Besides, lots of decompilers cannot be integrated with other programs because they do not have proper command line support.

DaaS aims to solve all those problems at the same time. The most external layer of DaaS is docker-compose, so it can run on any OS with docker support. All the other components run inside docker so now we can integrate the decompiler with any program on the same computer. In addition, we developed an API to use DaaS from the outside, so you can also connect the decompiler with programs from other computers and use the decompiler remotely. In our particular case at a Threat Intelligence team, we needed to decompile thousands of samples received from different systems and send the results back, been able to distribute processing and dynamically scaling our capabilities.

Although the tool's modular architecture allows you to easily create workers for decompiling many different file types, we started with the most challenging problem: decompile .NET executables. To accomplish that, we used Wine on a Docker container to run Windows decompilers flawlessly on a linux environment. In addition, on Windows some programs create useless or invisible windows in order to work, so we needed to add xvfb (x11 virtual frame buffer; a false x11 environment) to wrap those decompilers and avoid crashes on our pure command line environment. This allows you to install DaaS in any machine without desktop environment and be able to use any decompiler anyway.


# Summarized features
- Automatized malware decompilation.
- Use decompilers designed for Windows or Linux on any operative system.
- Code designed in an extensible and comprehensible way, so everyone can add new decompilers.
- Support for lots of samples submited at the same time, thanks to asynchronous responses and a queue system.
- Support for binaries and python libraries to be used as decompilers.
- Decompilers that create windows work flawlessly on a CLI environment.
- Keep all decompilation results together in one place and download them whenever you want.
- Advanced statistics about decompiled samples.
- Upload a zip file with tons of samples at the same time.
- API


# What is happening behind scenes
This section contains two graphics of the most representative and complex use cases of the API. It aims to give the reader a better understanding of how DaaS work.
For more technical details, go to "documentation/specifications.md".

![File_Upload](documentation/file_upload.jpg?raw=true "File Upload")

![URL_Upload](documentation/url_upload.jpg?raw=true "URL Upload")


# Screenshots
![Main](documentation/old_screenshots/main.png?raw=true "Main")


![Main (processing)](documentation/old_screenshots/main_processing.png?raw=true "Main (processing)")


![Statistics001](documentation/old_screenshots/statistics001.png?raw=true "Statistics 001")


![Statistics002](documentation/old_screenshots/statistics002.png?raw=true "Statistics 002")


![Statistics003](documentation/old_screenshots/statistics003.png?raw=true "Statistics 003")


![Statistics004](documentation/old_screenshots/statistics004.png?raw=true "Statistics 004")


![Statistics005](documentation/old_screenshots/statistics005.png?raw=true "Statistics 005")


![Statistics006](documentation/old_screenshots/statistics006.png?raw=true "Statistics 006")

# About code and releases
* If you want to use daas, please look for releases or the [stable branch](https://github.com/codexgigassys/daas/tree/stable).
* Since September 6, 2019, only squashed pull requests will be committed to master. Previously, commits were done to master directly.

# How to install
Requirements:
Install [docker](https://docs.docker.com/install/) and [docker-compose](https://docs.docker.com/compose/) on any operative system.

Then you should download the latest stable version of DaaS:
```
mkdir daas && cd daas
git clone https://github.com/codexgigassys/daas/stable
cd daas
```
From now on, it's recommended to use the specific documentation for the version you downloaded.
You can find it [here](https://github.com/codexgigassys/daas/tree/stable).

Now you are on the folder with docker-compose.yml file. You can start DaaS whenever you want using:
```
sudo docker-compose up -d
sudo docker-compose exec api sh -c "python /daas/manage.py makemigrations daas_app"
sudo docker-compose exec api sh -c "python /daas/manage.py migrate"
```

In case you want to stop DaaS and start it again later, use the following commands:
```
sudo docker-compose stop
```
and
```
sudo docker-compose start
```

## Recomendations
- Enable swap memory for any server running a decompiler. This will avoid the system running out of memory while processing unsually big samples.

# Increase Security

DaaS is an open source software, so some passwords and keys used here can be seen by everyone. It's recommended to change them manually for your production environments.
That changes are not necessary for DaaS to work, so you can skip this section if you want.

## Django configuration

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

## Database Password

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


# Adding new decompilers
## Naming conventions
First we need to define an string related to the file type we want to decompile. For example, if we want to add an APK decompiler, that string could be "apk".
This string will be the *identifier* of the worker/decompiler we are adding, and will be very important in the following steeps. It should be lower case and only contain letters between 'a' and 'z'. Avoid upper case letter, numbers and symbols.
For the moment, you don't need to save it in any configuration file.

## Dockerization
### Docker File
We need to create a docker image for the decompiler.
For that purpose, create a copy of *templateWorkerDockerfile* on DaaS root directory and rename it. This will be your decompiler's docker file.
It will look like this:
./yourDecompilerWorkerDockerfile:
```
FROM python:3.7.4-stretch
RUN mkdir /daas
WORKDIR /daas
ENV PYTHONUNBUFFERED=0
COPY requirements_worker.txt /tmp/requirements_worker.txt
RUN pip install --upgrade pip && \
    pip --retries 10 install -r /tmp/requirements_worker.txt


# Generic
RUN apt-get update && \
    apt-get install --no-install-recommends -y build-essential apt-transport-https && \
    apt-get install --no-install-recommends -y gnutls-bin \
        host \
        unzip \
        xauth \
        xvfb \
        zenity \
        zlib1g \
        zlib1g-dev \
        zlibc && \
    rm -rf /var/lib/apt/lists/* && \
    apt-get clean

```

Here you will need to know how to create a docker file. It's recommended to just let that generic stuff as is, and add your changes below.
For instance, in the flash decompiler we added some lines to install the decompiler:
```
FROM python:3.7.4-stretch
# ... (same as in the previous example)


# Generic
RUN apt-get clean && \
# ... (same as in the previous example)


##### LINES ADDED FOR FLASH DECOMPILER #####
# Flash
RUN mkdir /jre
ADD ./utils/jre /jre
RUN apt-get update && \
    apt-get install --no-install-recommends -y swftools && \
    apt-get install --no-install-recommends -y \
        java-common \
        libasound2 \
        libgl1 \
        libxtst6 \
        libxxf86vm1 && \
    rm -rf /var/lib/apt/lists/* && \
    apt-get clean
RUN dpkg -i /jre/oracle-java8-jre_8u161_amd64.deb && \
    rm -f -v /jre/oracle-java8-jre_8u161_amd64.deb && \
    rm -rf /var/lib/apt/lists/* && \
    apt-get clean

# Download ffdec
RUN wget -nv --no-check-certificate https://www.free-decompiler.com/flash/download/ffdec_10.0.0.deb -O /tmp/ffdec.deb && \
    dpkg -i /tmp/ffdec.deb && \
    rm -f /tmp/ffdec.deb && \
    rm -rf /var/lib/apt/lists/* && \
    apt-get clean
```
Other decompilers are easier to install. That will depend on what decompiler do you want to use.

If you can import the decompiler as a python library, then installing it will be reduced to only add the following line at the end of your docker file:
```
RUN pip install <your decompiler's package name>
```

### Docker Compose
Then you need to go to *docker-compose.yml*:
./docker-compose.yml
```
version: '3.7'
services:
  api:
    # ...

  redis_task_queue:
    # ...

  redis_statistics:
    # ...

  db:
    # ...

  pe_worker:
    # ...

  flash_worker:
    build:
      context: .
      dockerfile: flashWorkerDockerfile
    command: bash -c "rq worker --path / --url redis://daas_redis_task_queue_1:6379/0 flash_queue --name agent_$$(hostname -I | cut -d' ' -f1)_$$(echo $$RANDOM)__$$(date +%s)"
    volumes:
      - ./decompilers:/daas
    tmpfs:
      - /tmpfs
    links:
      - redis_task_queue
      - syslog
    logging:
      driver: syslog
      options:
        syslog-address: "udp://127.0.0.1:5514"
        tag: "flash_worker"

  syslog:
    # ...
```

We hide everything on the above example except the part related to flash decompiler to show only the most relevant section for the current example: flash_worker.

To add your own decompiler, you will need to add another section on *docker-compose.yml*.
Here is a template:
```
  your_decompiler_worker:
    build:
      context: .
      dockerfile: yourDecompilerWorkerDockerfile # this should match the name of the docker file you recently created.
    # In the following line replace "file_type_queue" by "apk_queue" for instance, if you are creating an apk plugin.
    command: bash -c "rq worker --path / --url redis://daas_redis_1:6379/0 <identifier>_queue --name agent_$$(hostname -I | cut -d' ' -f1)_$$(echo $$RANDOM)__$$(date +%s)"
    volumes:
      - ./decompilers:/daas
    tmpfs:
      - /tmpfs
    links:
      - redis_task_queue
      - syslog
    logging:
      driver: syslog
      options:
        syslog-address: "udp://127.0.0.1:5514"
        tag: "<identifier>_worker" # Change this too. You are able to use any tag, for instance: "apk_worker".
```
You only need to change "dockerfile", "command" and "tag". However, if you like to customize it more, you are able to.
Every time "<identifier>" appears, it should be replaced by you identifier (previously defined by you on the first steep).

At this point, the hardest part is already finished.

## Create a classifier
Now you need a classifier, to choose what samples will be sent to your decompiler:
./daas/daas_app/utils/classifiers.py:
```
from .file_utils import mime_type, has_csharp_description, pe_mime_types, flash_mime_types, apk_mime_types,\
    java_mime_types, zip_and_jar_shared_mime_types, has_java_structure, maybe_zip_mime_types, has_zip_structure


def pe_classifier(data):
    return mime_type(data) in pe_mime_types and has_csharp_description(data)


def flash_classifier(data):
    return mime_type(data) in flash_mime_types

# ...
```

This function receives the sample binary data and returns a boolean to say whether it should be sent to the processor we are creating or not.
The mime type is usually fine, so you can use an already defined classifier if there is one.

Be careful! the function should be named under the following format: <identifier>_classifier
For instance: "apk_classifier".


## Configure the decompiler
Here you should add basic information about the decompiler and how to run it.
If your decompiler is installed on your system as a package (regardless whether it needs wine or not), follow the instructions of 2.2A
If you use a python library, read the instructions of 2.2B instead

### Binary decompiler
Look for:
./daas/daas_app/decompiler_configuration/{csharp/flash/java}.py (any file will do):
```
csharp = {'sample_type': 'C#',
          'identifier': 'pe',
          'decompiler_name': 'Just Decompile',
          'requires_library': False,
          'decompiler_class': "CSharpDecompiler",
          'processes_to_kill': [r'.+\.exe.*'],
          'nice': 2,
          'timeout': 120,
          'decompiler_command': "wine /just_decompile/ConsoleRunner.exe \
                                '/target: @sample_path' \
                                '/out: @extraction_path'",
          'source_compression_algorithm': 'xztar',
          'version': 2}
```
Here we have a list with all available configurations ("config") and two specific configs for C# and flash decompilers.

You will need to add a new configuration at "/daas/daas_app/decompiler_configuration/<<any_file_name_you_want>>.py". They are technically a python dictionaries, but they look like JSONs.
You don't need to known python, just fulfill the fields of your interest as you would do with JSON files.
For instance, we will add a configuration for an APK decompiler:
/daas/daas_app/decompiler_configuration/apk.py:
```
# add your settings here.
apk = {'sample_type': 'APK',
       'identifier': 'apk',
       'decompiler_name': 'Random APK Decompiler',
       'requires_library': False,
       'decompiler_command': "random_apk_decompiler @sample_path @extraction_path"
       'version': 1}
```
We fulfilled only required fields. Here is a list of all available fields with their usage details:


| Field  | Type | Description | Default | Required to change |
| ------------- | ------------- | ------------- | ------------- | ------------- |
| sample_type | String | File type. For example: "APK". Usually the same as your identifiers, but you are able to use symbols and upper case here. | - | Yes |
| extension | String | The extension for the files in case the decompiler needs it. For example "jar". Usually you don't need to change this setting. | sample | No |
| identifier | String | File type. For example: "apk". This is the identified you defined at the start. | - | Yes |
| decompiler_name | String | Decompiler's name. Use the name you want to. It doesn't need to match your decompiler's file name. | - | Yes |
| decompiler_class | String | Decompiler Class in case you know Python and want to add some custom logic. Not needed in most of the cases. | - | No |
| requires_library | Boolean | Set it to 'False' (without quotes). | - | Yes |
| decompiler_command | String | A bash command to run the decompiler. Use single quotes for arguments with spaces. The decompiler will need a path with the file and probably a path to extract the files to. Use @sample_path and @extraction_path respectively instead of real paths. For example: "echo 'hello world'" or "decompiler_binary --input @sample_path --output @extraction_path". | - | Yes |
| version | Integer | Version of you configuration. Every time you change your configuration or your docker file, you should also increase this number by one. This is used to detect what samples were processed with older versions of certain decompilers. | - | No |
| nice_value | Integer | Priority of the process (see linux nice command). Zero is the default priority. | 0 | No |
| timeout_value | Integer | Timeout in seconds. Use zero or a negative number to disable timeout. | 120 | No |
| custom_current_working_directory | String | The current working directory used by python subprocess library. Probably you don't need to change this. | Decompilation directory (same as @extraction_path) | No |
| creates_windows | Boolean | Set it to True if you decompiler creates windows, even if they are invisible (common on some Windows programs). | False | No |
| processes_to_kill | List of regular expressions | List of regular expressions sent to pkill after the decompilers runs. Use this only if you have lots of zombie processes. | [] | No |


Then you need to edit "/daas/daas_app/decompiler_configuration/__init__.py", adding a new line with your decompiler:
```
from .csharp import csharp as _csharp
from .flash import flash as _flash
from .java import java as _java
from .apk import apk as _apk  # Your new line should look like this one.

configurations = [_csharp, _flash, _java, _apk]  # Add also the imported file here!
```


### Library decompiler
Support for library decompilers is currently deprecated as it was unused.
Look for older versions of DaaS to use library based decompilers, or open an issue requesting support.


## Optional steps
### Add an icon for your file type
Just add an icon named <identifier>.png (for instance: apk.png) at "./daas/daas_app/static/images/file_types/"
You will probably need to clear your browser cache to see the changes.


# DaaS architecture
![Daas Architecture](https://github.com/codexgigassys/daas/blob/master/daas_architecture.jpeg)


# DaaS Thanks

We would like to thanks the authors of the following tools, coming from other projects:

- Just Decompile (Telerik): https://www.telerik.com/products/decompiler.aspx
- JPEXS Free Flash Decompiler (Jindra Petřík): https://github.com/jindrapetrik/jpexs-decompiler
- CRF (Lee Benfield): http://www.benf.org/other/cfr/

In addition, we want to give thanks to the following conferences for accepting DaaS to be presented: 
- [EkoParty](https://www.ekoparty.org/), were we presented DaaS under ['ekolabs'](https://github.com/ekoparty/ekolabs) section in 2018.
- [Black Hat Asia](https://www.ekoparty.org/), were we presented DaaS under ['arsenals'](https://www.blackhat.com/asia-19/arsenal/schedule/#tab/thursday) section in 2019.


# Licence Notice
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

The license apply to all folders on this repository, except for:
- Files and folders in at "/utils/just_decompile". See the licence present on that folder for those files. There are also links to the source code if you are interested.
- Files located at "/daas/daas_app/static/images/file_types/".
