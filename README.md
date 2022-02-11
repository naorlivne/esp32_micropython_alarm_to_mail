# micropython_alarm_to_mail

Got mad at the cost the phone company requested for a landline phone where all I really needed it for was for the house alarm to ring me up when the alarm went off (who uses a landline phone anyway?).

The fix was to build this project and use it to send an email & telegram message when the alarm goes off, I've also added it with an alarm should the electrical box where the board is located heats up (only work on certain esp32 chips as not all have the internal temperature sensor) & writes healthchecks pings to influxdb.

## Features

* Send an email when the alarm goes off
* Send a telegram message when the alarm goes off
* sends healthchecks pings to influxdb
* alarm should the electrical box where the board is located heats up

## bill of materials

* esp32 board
* dc to dc step down converter (I used XL6009)
* USB power adapter & cable (to power the esp32 board)
* Some wires

## Installation

### electronics
.The electronic connections is quite simple:
![Wiring_diagram](electronics/diagram.jpg?raw=true)

1. Power the ESP32 up with the USB power adapter 
2. If you use a variable convertor use a multimeter and a screwdriver to adjust the potentiometer so that the output voltage is ~3v (input voltage is ~12v for my siren but check your alarm guide to yours)
3. Connect the dc to dc converter out pins to the board (- to gnd, + to the PIN your code is configured as `PORT_CONNECTED_TO_SIREN` default `32`)
4. the converter in pins should be connected to your alarm exterior siren (mine was named `BELL+` & `BELL-`, check your alarm guide for yours).

### the code
1. Flush your esp32 to [run MicroPyhton](https://docs.micropython.org/en/latest/esp32/tutorial/intro.html)
2. change all the variables in `main.py` to your needs (sorry but Micropython doesn't yet have an easy way to pass envvars outside the code)
3. upload `main.py` & `umail.py` to your esp32

Now everytime the alarm goes off You will get alerted via email & telegram.