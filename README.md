# Picontroller

Picontroller is a tool orchestrating rpi picos, their sensors and actuators, and a hub running on a server, via a simple API.

## Idea

Each of your picos have scripts from `pico` directory in their memory. Each contain a configuration file, which describes all the devices and network settings. Each pico has a file containing their own IP address in the network. A server connected to the same network communicates via TCP with picos able to send a request, asking for readings from sensor or requesting actuator action. Each "device", which is for example a humidity sensor or a servo, has it's unique name and can be requested by the user, while routing via specific picos is handled by the hub.


