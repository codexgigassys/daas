# DaaS
[![Circle CI](https://circleci.com/gh/codexgigassys/daas.png?style=shield)](https://circleci.com/gh/codexgigassys/daas)

# Index
- [What is DaaS?](#what-is-daas)
- [Summarized features](#summarized-features)
- [Screenshots](#screenshots)
- [How to install](#how-to-install)
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
    - [Optional steeps](#optional-steeps)
        - [Add an icon for your file type](#add-an-icon-for-your-file-type)
- [DaaS architecture](#daas-architecture)
- [DaaS Thanks](#daas-thanks)
- [Licence Notice](#licence-notice)


# What is DaaS
"Decompilation-as-a-Service" or "DaaS" is a tool designed to change the way of file decompiling. An analyst usually decompiles malware samples one by one using a program with a GUI. That's pretty good when dealing with a few samples, but it becomes really tedious to do with larger amounts. Not to mention if you have to decompile different types of files, with different tools and even different operating systems. Besides, lots of decompilers cannot be integrated with other programs because they do not have proper command line support.

DaaS aims to solve all those problems at the same time. The most external layer of DaaS is docker-compose, so it can run on any OS with docker support. All the other components run inside docker so now we can integrate the decompiler with any program on the same computer. In addition, we developed an API to use DaaS from the outside, so you can also connect the decompiler with programs from other computers and use the decompiler remotely. In our particular case at Deloitte Threat Intelligence team, we needed to decompile thousands of samples received from different systems and send the results back, been able to distribute processing and dinamically scaling our capabilities.

Although the tool's modular architecture allows you to easily create workers for decompiling many different file types, we started with the most challenging problem: decompile .NET executables. To accomplish that, we used Wine on a Docker container to run Windows decompilers flawlessly on a linux environment. In addition, on Windows some programs create useless or invisible windows in order to work, so we needed to add xvfb (x11 virtual frame buffer; a false x11 environment) to wrap those decompilers and avoid crashes on our pure command line environment. This allows you to install DaaS in any machine without desktop environment and be able to use any decompiler anyway.


# Summarized features
- Automatized malware decompilation.
- Use decompilers designed for Windwos or Linux on any operative system.
- Code designed in an extensible and comprehensible way, so everyone can add new decompilers.
- Support for lots of samples submited at the same time, thanks to asynchronous responses and a queue system.
- Support for binaries and python libraries to be used as decompilers.
- Decompilers that create windows work flawlessly on a CLI environment.
- Keep all decompilation results together in one place and download them whenever you want.
- Advanced statistics about decompiled samples.
- Upload a zip file with tons of samples at the same time.
- API


# Screenshots
![Main](documentation/main.png?raw=true "Main")


![Main (processing)](documentation/main_processing.png?raw=true "Main (processing)")


![Statistics001](documentation/statistics001.png?raw=true "Statistics 001")


![Statistics002](documentation/statistics002.png?raw=true "Statistics 002")


![Statistics003](documentation/statistics003.png?raw=true "Statistics 003")


![Statistics004](documentation/statistics004.png?raw=true "Statistics 004")


![Statistics005](documentation/statistics005.png?raw=true "Statistics 005")


![Statistics006](documentation/statistics006.png?raw=true "Statistics 006")


# How to install
Requirements:
Install [docker](https://docs.docker.com/install/) and [docker-compose](https://docs.docker.com/compose/) on any operative system.

Then you should download the latest stable version of DaaS:
```
mkdir daas && cd daas
git clone https://github.com/codexgigassys/daas/stable
cd daas
```
From now on, it's recommended to use the specific documentation for that version.
You can found it [here](https://github.com/codexgigassys/daas/tree/stable).

Now you are on the folder with docker-compose.yml file. You can start DaaS whenever you want using:
```
sudo docker-compose up -d
```

In case you want to stop DaaS and start it again later, use the following commands:
```
sudo docker-compose stop
```
and
```
sudo docker-compose start
```

# Increase Security

DaaS is an open source software, so some passwords and keys used here can be seen by everyone. It's recommended to change them manually.
This changes are not necessary for DaaS to work, so you can skip this section if you want.

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
First, we need to create a docker image for the decompiler.
For that purpose, create a copy of *templateWorkerDockerfile* on DaaS root directory and rename it. This will be your decompiler's docker file.
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
# ... (same as in the previous example)


# Added for flash decompiler:
ADD ./utils/jre /jre


# Generic
RUN apt-get clean && \
# ... (same as in the previous example)



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
Other decompilers are easier to install. That will depend on what decompiler you want to use.

If you can import the decompiler as a python library, then installing it will be reduced to only add the following line at the end of your docker file:
```
RUN pip install <your decompiler's package name>
```

### Docker Compose
Then you need to go to *docker-compose.yml*:
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

We commented everything on the above example except the part related to flash decompiler to show only the most relevant section: flash_worker.

To add your own decompiler, you will need to add another section on *docker-compose.yml*.
Here is a template:
```
  your_decompiler_worker:
    build:
      context: .
      dockerfile: yourDecompilerWorkerDockerfile # this should match the name of the docker file you recently created.
    # In the following line replace "file_type_queue" by "apk_queue" for instance, if you are creating an apk plugin.
    command: bash -c "sleep 15 && pip --retries 10 install -r /daas/pip_requirements_worker.txt && rq worker --path /daas/daas/daas_app --url redis://daas_redis_1:6379/0 <identifier>_queue --name agent_$$(hostname -I | cut -d' ' -f1)_$$(echo $$RANDOM)__$$(date +%s)"
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
        tag: "<identifier>_worker" # Change this too. You are able to use any tag, for instance: "apk_worker".
```
You only need to change "dockerfile", "command" and "tag". However, if you like to customize it more, you are able to.
Every time "<identifier>" appears, it should be replaced by you identifier (previously defined by you on the first steep).

At this point, the hardest part is already finished.

## Create a classifier
Now you need a classifier, to choose what samples will be sent to your decompiler:
./daas/daas_app/utils/classifiers.py:
```
from .classifier_utils import mime_type, pe_mime_types, flash_mime_types


def pe_classifier(data):
    return mime_type(data) in pe_mime_types


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
If your decompiler is installed on your system as a package or requires wine, follow the instructions of 2.2A
If you use a python library, read the instructions of 2.2B instead

### Binary decompiler
Look for:
./daas/daas_app/decompilers/decompiler_config.py:
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
          'version': 1}

flash = {'sample_type': 'Flash',
         'identifier': 'flash',
         'decompiler_name': 'FFDec',
         'requires_library': False,
         'timeout': 720,
         'decompiler_command': "ffdec -onerror ignore -timeout 600 -exportTimeout 600 \
                                -exportFileTimeout 600 -export all \
                                @extraction_path @sample_path",
         'version': 1}

configs = [csharp, flash]
```
Here we have a list with all available configurations ("config") and two specific configs for C# and flash decompilers.

You will need to add a new configuration here. They are technically a python dictionaries, but they look like JSONs.
You don't need to known python, just fulfill the fields of your interest as you do with JSON configuration files.
For instance, we will add a configuration for an APK decompiler:
```
csharp = # ...

flash = # ...

# add your settings here.
apk = {'sample_type': 'APK',
       'identifier': 'apk',
       'decompiler_name': 'Random APK Decompiler',
       'requires_library': False,
       'decompiler_command': "random_apk_decompiler @sample_path @extraction_path"
       'version': 1}
       
       
configs = [csharp, flash, apk] #  add your new configuration to the list!
```
We fulfilled only required fields. Here is a list of all available fields with their usage details:


| Field  | Type | Description | Default | Required to change |
| ------------- | ------------- | ------------- | ------------- | ------------- |
| sample_type | String | File type. For example: "APK". Usually the same as your identifiers, but you are able to use symbols and upper case here. | - | Yes |
| identifier | String | File type. For example: "apk". This is the identified you defined at the start. | - | Yes |
| decompiler_name | String | Decompiler's name. Use the name you want to. It doesn't need to match your decompiler's file name. | - | Yes |
| requires_library | Boolean | Set it to 'False' (without quotes). | - | Yes |
| decompiler_command | String | A bash command to run the decompiler. Use single quotes for arguments with spaces. The decompiler will need a path with the file and probably a path to extract the files to. Use @sample_path and @extraction_path respectively instead of real paths. For example: "echo 'hello world'" or "decompiler_binary --input @sample_path --output @extraction_path". | - | Yes |
| version | Integer | Version of you configuration. Every time you change your configuration or your docker file, you should also increase this number by one. This is used to detect what samples were processed with older versions of certain decompilers. | - | No |
| nice_value | Integer | Priority of the process (see linux nice command). Zero is the default priority. | 0 | No |
| timeout_value | Integer | Timeout in seconds. Use zero or a negative number to disable timeout. | 120 | No |
| custom_current_working_directory | String | The current working directory used by python subprocess library. Probably you don't need to change this. | Decompilation directory (same as @extraction_path) | No |
| creates_windows | Boolean | Set it to True if you decompiler creates windows, even if they are invisible (common on some Windows programs). | False | No |
| processes_to_kill | List of regular expressions | List of regular expressions sent to pkill after the decompilers runs. Use this only if you have lots of zombie processes. | [] | No |

### Library decompiler

Look for:
./daas/daas_app/decompilers/decompiler.py:
```
class YourFileTypeWorker(LibraryBasedWorker): # given a proper name to the class
    def decompile(self):
        """ Should be overriden by subclasses.
        This should return output messages (if there are some), or '' if there isn't anything to return. """
```
The class should be named using the following pattern: <identifier with only the first letter in upper case>Decompiler.
For instance: ApkDecompiler, JavaDecompiler, FlashDecompiler, ...


Then follow the instructions of "decompile" method and override it.
When you need access to the sample or set a directory to decompile, use the following methods respectively: 
- self.get_tmpfs_file_path()
- self.get_tmpfs_folder_path()

For example:
./daas/daas_app/decompilers/decompiler.py:
```
class ApkDecompiler(LibraryBasedWorker):
    def decompile(self):
        return apk_decompiler_library(file=self.get_tmpfs_file_path(),
                                      extract_to=self.get_tmpfs_folder_path())
```


Now look for:
./daas/daas_app/decompilers/decompiler_config.py:
```
csharp = {'sample_type': 'C#',
          'identifier': 'pe',
          'decompiler_name': 'Just Decompile',
          'requires_library': False,
          'processes_to_kill': [r'.+\.exe.*'],
          'nice': 2,
          'timeout': 120,
          'decompiler_command': "wine /just_decompile/ConsoleRunner.exe \
                                '/target: @sample_path' \
                                '/out: @extraction_path'",
          'version': 1}

flash = {'sample_type': 'Flash',
         'identifier': 'flash',
         'decompiler_name': 'FFDec',
         'requires_library': False,
         'timeout': 720,
         'decompiler_command': "ffdec -onerror ignore -timeout 600 -exportTimeout 600 \
                                -exportFileTimeout 600 -export all \
                                @extraction_path @sample_path",
         'version': 1}

configs = [csharp, flash]
```
Here we have a list with all available configurations ("config") and two specific configs for C# and flash decompilers.

You will need to add a new configuration here. They are technically a python dictionaries, but they look like JSONs.
You don't need to known python. Just fulfill the fields of your interest as you would do with a JSON file.
For instance, we will add a configuration for an APK decompiler:
```
csharp = # ...

flash = # ...

# Add your settings here.
apk = {'sample_type': 'APK',
       'identifier': 'apk',
       'decompiler_name': 'Random APK Decompiler',
       'requires_library': True,
       'version': 1}
       
       
configs = [csharp, flash, apk] #  add your new configuration to the list!
```
We fulfilled all available fields for this kind of decompiler. Here is a list of all available fields with their usage details:


| Field  | Type | Description | Default | Required to change |
| ------------- | ------------- | ------------- | ------------- | ------------- |
| sample_type | String | File type. For example: "APK". Usually the same as your identifiers, but you are able to use symbols and upper case here. | - | Yes |
| identifier | String | File type. For example: "apk". This is the identified you defined at the start. | - | Yes |
| decompiler_name | String | Decompiler's name. Use the name you want to. It doesn't need to match your decompiler's file name. | - | Yes |
| requires_library | Boolean | Set it to 'True' (without quotes). | - | Yes |
| version | Integer | Version of you configuration. Every time you change your configuration or your docker file, you should also increase this number by one. This is used to detect what samples were processed with older versions of certain decompilers. | 0 | No |

## Optional steeps
### Add an icon for your file type
Just add an icon named <identifier>.png (for instance: apk.png) at /daas/static_resources/images/file_types/.
You will probably need to clear your browser cache to see the changes.


# DaaS architecture
![Daas Architecture](https://github.com/codexgigassys/daas/blob/master/daas_architecture.jpeg)


# DaaS Thanks

We would like to thanks the authors of the following tools, coming from other projects:

- Just Decompile (Telerik): https://www.telerik.com/products/decompiler.aspx
- JPEXS Free Flash Decompiler (Jindra Petřík): https://github.com/jindrapetrik/jpexs-decompiler

Thanks to [EkoParty](https://www.ekoparty.org/) for accepting the tool to be presented under ['ekolabs'](https://github.com/ekoparty/ekolabs) section in 2018.


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

For the files and folders in the "/utils/just_decompile" folder, see the licence present on that folder. There are also links to the source code if you are interested.
