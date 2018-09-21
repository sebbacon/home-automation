# Heating

We're a family of four. Each day has different rythmns for each of us. We move between rooms in fairly predictable patterns.

I like it cool in my bedroom all day and night. The kids need their rooms to be a little warm when they get up in the week, and for longer at the weekends. The living room should be comfortable in the evening.  And so on.

The default heating algorithm, "heat the entire house based on the temperature of the living room and an arbitrary timer", means we waste a lot of energy.

The solution is to have a custom programme on every single radiator in the house.

This setup cost me about £200, and several days of my life in tweaking and tinkering.  I won't know for a year how much it saves me on energy bills, but I'm guessing quite a lot.

Basic controls from my phone:

<img src="https://user-images.githubusercontent.com/211271/45709855-f07f1800-bb7c-11e8-902a-5212b93467c6.png" alt="openhab screenshot on phone" width="300px">

Lots of nice graphs for tracking energy usage and heat levels:

<img src="https://user-images.githubusercontent.com/211271/45709706-8f574480-bb7c-11e8-84de-a6f4bba3b4bf.png" alt="screenshot of heating graph" width="300px">

## Hardware setup

It's something like this: <img src="https://user-images.githubusercontent.com/211271/45876801-ab80fe80-bd93-11e8-9c4f-a5293d8861e5.png" alt="crappy schematic of the system" width="300px">

The most expensive part is the thermostatic radiator control system.

The [EQ Max system](https://www.conrad-electronic.co.uk/ce/en/overview/0812043/MAX-Wireless-Heating-Control) is the best value system out there, and apparently fairly reliable.

The [thermostat heads](https://www.conrad-electronic.co.uk/ce/en/product/1378424/MAX-Wireless-thermostat-head-Basic?ref=list) communicate over 868MHz RF to a ["Cube" device](https://www.conrad-electronic.co.uk/ce/en/product/560896/MAX-Cube-Lan-Gateway-Cube?ref=list). The Cube allows you to TRVs into rooms, set programs (e.g. *21 degrees centigrade between 0900 and 1300 on a Monday*),  check battery life, etc. The cube is controlled via Java software which runs as a web server on your computer. It is packaged for Windows and Mac but a community member has helpfully [repackaged it for Linux](https://github.com/shawn-ogg/maxapp_linux_installer). The protocol [has been reverse engineered](https://github.com/Bouni/max-cube-protocol), of which there are various implementations around the web.

Each head stores its program locally, which means they'll continue to work even when your Cube goes down.  They can be individually "boosted" with hardware buttons.

There's a nice decalcification feature, which will fully depress and release the pin that operates the radiator valve (once a week by default)

The default mode of operation is "automatic". This means each head will follow its programmed schedule. When you override the schedule (by increasing the temperature), this change will stick until the next programmed temperature change, when the head will revert to the programmed settings.

A wall thermostat (for better ambient temperature measurement, and convenient setting of multi-radiator groups), and window sensors (which by default will automatically dial down your heating for 10 minutes when a window opens) are also available.

By all accounts the cube is a little buggy and forgets its associations between the TRV devices and the named programs. Instead of using the cube, you can consider using the open source `culfw` software, and either (a) flashing the cube ([German instructions](https://forum.fhem.de/index.php/topic,38404.0.html?PHPSESSID=g9gjrbkpt56p5qnv1on6nnlr16)) or (b) using your own CUL module and [flashing that](https://forum.pimatic.org/topic/2483/pimatic-maxcul-and-max-cube-with-aculfw-acting-as-cul/45).


### Random observations

When playing with scripting, I found TRVs would randomly stop responding. It turns out this is because of the "1% rule" - each RF band has a "duty cycle" which is the maximum ratio of time on the air per hour. Basically, 1% means you can speak 36s per hour.

### Heads

The heads use M30 x 1.5mm standard thread size which fits most modern radiators. If you're lucky, you can just unscrew the union nut by hand (or with a bit of help from a plumber's wrench) and attach the EQ-MAX TRV with its own union nut.

Older radiators are more of a pain. Two of the radiators in my house are Comap Westherm which uses M28 x 1mm. You'll have to hope you can find an adaptor (I could), or you'll need to get a plumber to change the radiator fittings for you. Here's a [handy list of adapter sizes](https://energenie4u.co.uk/res/pdfs/Valve%20Adaptor%20List%20V5.pdf).  (The heads also come with a Danfoss RA adaptor which is rarely used in the UK)

Sometimes you'll see an `F2` error message on the adaptor after fitting. This means it's not seated properly. I gave older valves a squirt with some lubricant and jiggled the little stud that opens and closes the valve with some soft hammer taps. Where there's a long thread you have to tighten the nut a bit further than you expect to get a snug internal fit against the stud. On the radiators wheren I used adaptors, the problem was the pin in the adaptor was not snug against the inner pin (on the radiator), so I placed a 1p coin inside the adaptor, and this seemed to work


### Wall thermostat

For my main living space, which is open plan with the kitchen, I bought a [wall thermostat](https://www.conrad-electronic.co.uk/ce/en/product/560920/MAX-Wireless-wall-mount-thermostat-MAX?queryFromSuggest=true).  It's useful because:

* The radiator valves only report back to the cube when their state changes, but the thermostat updates every 90 seconds or so. It's nice to get more granular data about where you spend most of your time
* You can put it on the wall near where you sit: it will give a more accurate idea of the ambient temperature of the room, as opposed to a valve mounted on the radiator
* It acts as a simple hardware switch for temporarily boosting the temperature. This is particularly useful in a room with more than one radiator.

### Raspberry Pi and relay

I have a combi boiler, which needs to be turned off when there is no heat demand.  I did this with a Raspberry Pi 3+ and a relay. I'm not particularly knowledgable about electronics, so I opted for a pre-built relay board ([ModMyPi PiOT Relay Board](https://www.modmypi.com/raspberry-pi/relays-and-home-automation-1032/relay-boards-1033/modmypi-piot-relay-board)) and [case](https://www.modmypi.com/raspberry-pi/cases-183/raspberry-pi-b-plus2-and-3-cases-1122/cases-for-hats-and-boards-1133/modmypi-piot-relay-board-case-b-plus23) rather than faffing around with resistors, dealing with GPIO chatter, etc.  I'm pleased with the quality and it was straightforward to assemble and use.

I opted to use the Pi as the home automation hub (running OpenHabian), and I've plugged a 4TB USB drive into a USB port for backups, and doubling up as a simple NAS.

The relay takes the place of the old thermostatic wall switch. For me, this had been wired from the Combi Boiler with a neutral and two lives. The switch breaks the live wire; the neutral was there to supply power to the thermostat.  Replacing the wall switch involved cutting back and taping the neutral (not needed), and then attaching the live to COM ("common") and NC ("normally closed") terminals on one of the relays.  The PiOT Relay Board has a nice interface for binding a relay to a GPIO which can then be addressed from the Pi.

## Software setup

There's a few open source home automation hubs out there. I picked Openhab2 because it looked OK and has EQ3-Max! integration.


### Cube and thermostatic heads setup

To start with, you have to pair the thermostatic heads (and wall thermostat) with the cube, so it knows what it can address (the documentation calls this "teaching-in"). You need to start the Max! software to access the Cube's control interface.  This is Java software which runs as a web server on your computer that you access using your web browser. It is packaged for Windows and Mac but a community member has helpfully [repackaged it for Linux](https://github.com/shawn-ogg/maxapp_linux_installer).

You probably don't *have* to use that software: the protocol [has been reverse engineered](https://github.com/Bouni/max-cube-protocol), of which there are various implementations around the web, but none of them (that I've found) are complete. Most of these can report on current thermostat state and set current temperature, but that's all.

Once you've taught-in the thermostats, you can set their daily schedule: up to 7 heat/time pairs per day, per thermostatic head. The EQ-Max! software is very clunky for this, particularly as you typically want to do a lot of cut-and-paste, so I've [added a command to python-maxcube-api](https://github.com/sebbacon/python-maxcube-api/tree/add-program-setting) to allow you to save and set programmes in JSON.


### openHABian

[openHABian](https://www.openhab.org/docs/installation/openhabian.html) is a Raspberry Pi SD image which includes OpenHab and some other somewhat useful configuration.

I ended up tweaking it quite a lot so not sure I'd start with it next time, but it's OK.  It's based on Raspbian Lite and comes with reasonable install instructions.


### OpenHab2

The OpenHab integration allows you to:

* Set individual thermostat temperatures
* Get "current" (see below) thermostat temperatures
* Get valve state (e.g. 65% open)
* Get battery state (i.e. a flag for if the battery is low)

One you have paired the thermostatic heads with the cube, you can progress to adding them as "things" in OpenHab2. Start by [adding the MAX! Binding](https://github.com/openhab/openhab2-addons/tree/master/addons/binding/org.openhab.binding.max), and take it from there. You'll have to read the openhab2 docs for full details, but the short version is:

* Find the setting in the Paper UI that automatically makes items (configuration > system > item linking > simple mode)
* Add the Cube by visiting the discovery inbox in the Paper UI
* Thermostats should start appearing in the inbox. Add them and they will appear as Items in the control panel

TODO: I'm not entirely sure if you actually have to set up things in the inbox as well as in files

### Grafana

### Boiler control

### Mobile phone

#### Tasker

#### Openhab client

## System administrivia

### Backups

### Email
