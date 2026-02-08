# Picontroller

Picontroller is a tool orchestrating rpi picos, their sensors and actuators,
and a hub with controller running on a server, via a simple API.

## The idea

Imagine that in your multi-room house you have old lamps with switches on their
power cords. You’re tired of reaching for them every time to turn them on or
off, as well as walking through all the rooms before leaving the house just to
check whether each one is turned off. You come up with the idea of installing a
small servo mechanism in each of these lamps that could turn them on and off.
You take a few Raspberry Pi Pico W boards out of the garage and realize that
each of them can be connected to your home Wi-Fi and enable remote control of
the servo mechanisms attached to the lamp switches. Without much hesitation,
you connect the servos and the boards.

However, connecting every time to a specific board on your home network and
remembering their IP addresses is tiring. So you use an old Raspberry Pi Zero W
that has been gathering dust in a box to set up a small server. Now you can
send requests to this server with content like “turn off the light in the large
room upstairs,” and it will forward the request to the correct board.

You are proud of your system. However, each board still has many free pins
available. In every room there are plants that need watering from time to time.
What if this could be done in a smilar manner? You place soil moisture sensors
in the pots, as well as servo mechanisms that dispense water. Now most of the
pins on each Raspberry Pi Pico board have a sensor or actuator connected to
them. Thanks to the software you wrote, you can ask your server for the soil
moisture readings from a selected sensor, and the server queries the
appropriate Pico board and the correct sensor connected to it. Wonderful! You
can water your plants throughout the house without even getting up from your
laptop.

You come up with a brilliant idea — what if the server watered the plants
automatically when the soil becomes too dry? You write a simple controller that
takes over checking the soil moisture for you. You can still check the readings
from each sensor or set the state of each servo mechanism using an API request
sent to the server. For now, you use a simple script to send network requests
via the CLI. It’s convenient, but it would be even better if the server also
exposed a web interface on your home network. So you write a simple web server
that statically generates a website based on the configuration files of your
sensor and actuator control system. Thanks to this, you can control the entire
system through a browser on your computer, smartphone, or even your TV!

This required a lot of work. If only there already existed a framework
implementing all these mechanisms. Using it, all the work would consist only of
creating a short configuration file describing your sensors and actuators, and
some simple logic defining when plants should be watered and at what time the
lights should turn off in the evening.

Luckily, such a framework exists — and it’s called picontroller.

## Let's run it - a kickstart guide

Your first setup will consist of one Pico board and your computer connected to
the same Wi-Fi network.

### Preparation

Picos are supposed to run python scripts. In order to make them do that, you
will have to upload the interpreter on them. You can download it from their
website. Just make sure that you upload the right interpreter (RPI for pico w
and RPI2 for pico 2 w). After downloading, press the bootsel button on the pico
and holding it connect to the computer via USB. Loose it. Use picotool to
upload the .uf2 file (sudo picotool load <name of the file>). Disconnect and
connect again to your computer.

On the computer, install mpremote via pip (pip install mpremote). For now we
assume Debian-based Linux system is your OS.

### Edit the configuration file

In the `configuration_files` directory you will find `configuration.json` file.
Edit it and pass your network's SSID (network's name), password and gateway
(router/access point IP adress). This file will be used by scripts on both your
computer and the pico board.

### Run the hub on your computer

Execute `run_controller` script on your computer. Keep it running.

### Upload modules and configuration files to pico

Open another terminal session. Make sure you are in the root directory of the
project. Execute `uprun` script when connected via USB to your pico. You should
see the files copied listed and a repl output should appear. Pico should
connect to the network.

Shortly after that the pico's LED will start to blink at frequency of around 1
Hz (1 blink every second). Don't worry if the intervals are not regular.

Blinking means that your computer already sends requests to blink every 1
second and the pico executes the requested action.

You can press ctrl+c on the terminal window with pico's repl. Pico will keep
running as long as it is connected to the power. It will also connect to the
network and listen for hub's requests every time it boots up.

### Use CLI script

The pico is blinking. The hub is running.

Edit `hub_ip.json` file and set `hub_ip` value to `127.0.0.1` (your localhost
address). The `cli` script will read it and connect to that address when
talking to the hub.

Execute `./cli get` command. A table showing current parameters should show up
after a while.

Now you can change the blinking interval. Execute `./cli set
main_loop_sleep_time_s 0.1` to update the hub's sleep time between main loop
iterations.

This change was not persistent. If you stop hub and run it again it will again
run with 1 second interval. To make persisten changes you need to save them.

To do that make sure after setting the interval to 0.1 s, execute command
`./cli save` to write that update to the file. If you `cat
configuration_files/configuration.json` you will see the change.

Congratulations! You know how to run it. Now you are ready to learn how to
adjust the configuration files and scripts to your needs.

## Writing your own configuraiton files and logic

### Write configuration file matching your hardware setup

### Write logic operating on the objects defined in configuration

## Inteded design

The framework is inteded to work as described below.

Each of your Pico boards has scripts from `pico` directory uploaded along the
python interpreter. Each board contains:

- python modules,
- configuration file, which describes all the devices and network settings - it
is the same file as the server has,
- IP address file. 

A server connected to the same network reads the same configuration file and
communicates via TCP with Picos. The server can send a request, asking for
readings from sensor or requesting actuator action. Each "device", which is for
example a humidity sensor or a servo, has it's unique name.

Hub running on the server does two things:

- sends requests to Picos
- handles user request by changing the zmq data store values.

