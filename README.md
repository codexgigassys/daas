# DaaS
## What is DaaS?
"Decompilation as a service" or "DaaS" is a program designed to change the way of file decompiling. An analyst usually decompile executables one by one using a program with a GUI under windows. That's a bit slow when we want to decompile lots of different files, and also can not be integrated with other programs because the decompiler uses a GUI and runs only on Windows Systems. DaaS aims to solve both problems at the same time. The most external layer of DaaS is docker-compose, so it can run on any OS with docker support. All the other components run inside docker so now we can integrate the decompiler with any program on the same computer. Also, we developed an API to use DaaS from the outside, so you can also connect the decompiler with programs from other computers and use the decompiler remotely.
Then we use wine and xvfb (x11 frame buffer; a false x11 enviroment) to wrap the c# decompiler and avoid any problem related to the GUI usage of different programs (some create useless or invisible windows in order to work, so we need to mock x11 to avoid crashes). This will allow you to install DaaS in any machine without desktop enviroment and use the decompiler anyway.
The decompiler we are using now is "Just Decompile", but with some tricks most of the decompilers should work.

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
along with Foobar.  If not, see https://www.gnu.org/licenses/gpl-3.0.en.html.

For the files and folders in the "/utils/just_decompile" folder, see the licence present on that folder. There are also links to the source code if you are interested.
