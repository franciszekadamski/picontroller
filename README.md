# Picontroller

Picontroller is a tool orchestrating rpi picos, their sensors and actuators, and
a hub with controller running on a server, via a simple API.

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

## Project structure

Each of your picos have scripts from `pico` directory in their memory. Each
contains a configuration file, which describes all the devices and network
settings. Each pico has a file containing their own IP address in the network. A
server connected to the same network communicates via TCP with picos able to
send a request, asking for readings from sensor or requesting actuator action.
Each "device", which is for example a humidity sensor or a servo, has it's
unique name and can be requested by the user, while routing via specific picos
is handled by the controller.

