# Heating

We're a family of four.  I like it cool in my bedroom all day and night. The kids need their rooms to be a little warm when they get up in the week, and for longer at the weekends. The living room should be comfortable in the evening.  And so on.

The UK's default heating algorithm, "heat the entire house based on the temperature of the living room and an arbitrary timer", means we waste a lot of energy. The solution is to have a custom programme on every single radiator in the house. This setup cost me about £200 (plus several days of time, but it was fun).  I won't know for a year how much it saves me on energy bills, but I'm guessing quite a lot.

Basic controls from my phone:

<img src="https://user-images.githubusercontent.com/211271/45709855-f07f1800-bb7c-11e8-902a-5212b93467c6.png" alt="openhab screenshot on phone" width="300px">

Lots of nice graphs for tracking energy usage and heat levels:

<img src="https://user-images.githubusercontent.com/211271/45709706-8f574480-bb7c-11e8-84de-a6f4bba3b4bf.png" alt="screenshot of heating graph" width="300px">

## Hardware setup

It's something like this:

<img src="https://user-images.githubusercontent.com/211271/45876801-ab80fe80-bd93-11e8-9c4f-a5293d8861e5.png" alt="crappy schematic of the system" width="300px">

The most expensive part is the thermostatic radiator control system.

The [EQ Max system](https://www.conrad-electronic.co.uk/ce/en/overview/0812043/MAX-Wireless-Heating-Control) is the best value system out there, and apparently fairly reliable. It's worth mentioning <a href="https://www.tado.com">Tado</a>, which  *appears* to do much of the following for you, but it's a lot more expensive.

The [thermostat heads](https://www.conrad-electronic.co.uk/ce/en/product/1378424/MAX-Wireless-thermostat-head-Basic?ref=list) communicate over 868MHz RF to a ["Cube" device](https://www.conrad-electronic.co.uk/ce/en/product/560896/MAX-Cube-Lan-Gateway-Cube?ref=list). The Cube allows you to TRVs into rooms, set programs (e.g. *21 degrees centigrade between 0900 and 1300 on a Monday*),  check battery life, etc. The cube is controlled via Java software which runs as a web server on your computer. It is packaged for Windows and Mac but a community member has helpfully [repackaged it for Linux](https://github.com/shawn-ogg/maxapp_linux_installer). The protocol [has been reverse engineered](https://github.com/Bouni/max-cube-protocol), of which there are various implementations around the web.

Each head stores its program locally, which means they'll continue to work even when your Cube goes down.  They can be individually "boosted" with hardware buttons.

There's a nice decalcification feature, which will fully depress and release the pin that operates the radiator valve (once a week by default)

The default mode of operation is "automatic". This means each head will follow its programmed schedule. When you override the schedule (by increasing the temperature), this change will stick until the next programmed temperature change, when the head will revert to the programmed settings.

A wall thermostat (for better ambient temperature measurement, and convenient setting of multi-radiator groups), and window sensors (which by default will automatically dial down your heating for 10 minutes when a window opens) are also available.

By all accounts the cube is a little buggy and forgets its associations between the TRV devices and the named programs. Instead of using the cube, you can consider using the open source `culfw` software, and either (a) flashing the cube ([German instructions](https://forum.fhem.de/index.php/topic,38404.0.html?PHPSESSID=g9gjrbkpt56p5qnv1on6nnlr16)) or (b) using your own CUL module and [flashing that](https://forum.pimatic.org/topic/2483/pimatic-maxcul-and-max-cube-with-aculfw-acting-as-cul/45).

A traditional setup turns all the radiators on and off with a thermostatic switch attached to the boiler (a combi-boiler in my case). This needs to be turned off automatically when there is no heat demand.  I did this with a Raspberry Pi 3+ and a relay.  I added a physical switch as an override

If the Raspberry Pi were to break, we'd want to to have confidence we could still turn the boiler on and off, so I added a physical switch which will bypass the Pi when turned on.  It looks like this:

<img src="https://user-images.githubusercontent.com/211271/45892046-f2381e00-bdbe-11e8-834f-0d0eaecc869a.png" alt="photo of pi, hard disk, override switch and boiler" width="300px">


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

I'm not particularly knowledgable about electronics, so I opted for a pre-built relay board ([ModMyPi PiOT Relay Board](https://www.modmypi.com/raspberry-pi/relays-and-home-automation-1032/relay-boards-1033/modmypi-piot-relay-board)) and [case](https://www.modmypi.com/raspberry-pi/cases-183/raspberry-pi-b-plus2-and-3-cases-1122/cases-for-hats-and-boards-1133/modmypi-piot-relay-board-case-b-plus23) rather than faffing around with resistors,  GPIO chatter, etc.  I'm pleased with the quality of this unit and case, and it was straightforward to assemble and use.

It makes sense to use the Pi as the home automation hub (running OpenHabian), and I've plugged a 4TB USB drive into a USB port for backups, and doubling up as a simple NAS.

The relay takes the place of the old thermostatic wall switch. My thermostat was wired from the combi-boiler with a neutral and two lives (refer to your boiler manual for details). The switch in the thermostat breaks the live; the neutral suppled power to the thermostat.  Replacing the old wall thermostat involved cutting back and taping the neutral (not needed), and then attaching the two lives to `COM` ("common") and `NO` ("normally open") terminals on one of the relays.  The PiOT Relay Board has a nice interface for binding a relay to a GPIO which can then be addressed from the Pi.

## Software setup

There's a few open source home automation hubs out there. I picked Openhab2 because it looked OK and has EQ3-Max! integration.


### Cube and thermostatic heads setup

To start with, you have to pair the thermostatic heads (and wall thermostat) with the cube, so it knows what it can address (the documentation calls this "teaching-in"). You need to start the Max! software to access the Cube's control interface.  This is Java software which runs as a web server on your computer that you access using your web browser. It is packaged for Windows and Mac but a community member has helpfully [repackaged it for Linux](https://github.com/shawn-ogg/maxapp_linux_installer).

Theoretically, you don't *have* to use that software: the protocol [has been reverse engineered](https://github.com/Bouni/max-cube-protocol), of which there are various implementations around the web, but none of them (that I've found) are complete. Most of these can report on current thermostat state and set current temperature, but that's all.

Once you've taught-in the thermostats, you can set their daily schedule: up to 7 heat/time pairs per day, per thermostatic head. The EQ-Max! software is very clunky for this, particularly as you typically want to do a lot of cut-and-paste, so I've [added a command to python-maxcube-api](https://github.com/sebbacon/python-maxcube-api/tree/add-program-setting) to allow you to save and set programmes in JSON.  I also used the official software to group the three radiators and the wall thermostat in our open plan living space into one room.

*Note*: When playing with scripting, I found TRVs would randomly stop responding. It turns out this is because of the "1% rule" - each RF band has a "duty cycle" which is the maximum ratio of time on the air per hour. Basically, 1% means you can speak 36s per hour.

### openHABian

[openHABian](https://www.openhab.org/docs/installation/openhabian.html) is a Raspberry Pi SD image which includes OpenHab and some other somewhat useful configuration.

I ended up tweaking it quite a lot so not sure I'd start with it next time, but it's OK.  It's based on Raspbian Lite and comes with reasonable install instructions.


### OpenHab2

The OpenHab2 MAX! Cube integration allows you to:

* Set individual thermostat temperatures
* Get "current" (see below) thermostat temperatures
* Get valve state (e.g. 65% open)
* Get battery state (i.e. a flag for if the battery is low)

One you have paired the thermostatic heads with the cube, you can progress to adding them as "things" in OpenHab2. Start by [adding the MAX! Binding](https://github.com/openhab/openhab2-addons/tree/master/addons/binding/org.openhab.binding.max), and take it from there. You'll have to read the openhab2 docs for full details, but the short version is:

* Find the setting in the Paper UI that automatically makes items (configuration > system > item linking > simple mode)
* Add the Cube by visiting the discovery inbox in the Paper UI
* Thermostats should start appearing in the inbox. Add them and they will appear as Items in the control panel

*TODO: I'm not entirely sure if you actually have to set up things in the inbox as well as in files. This is just the order I did it in. Check!*

Now you're ready to set up text-based configuration files which will allow you to:

* View and control the system from your phone
* Set up rules to turn the boiler on and off, email you when batteries are low, etc

Each thermostatic head has a 6-byte RF address and a 10-character serial number. Both of these can be inspected in the OpenHab Paper UI. The serial number is also on a sticker inside the battery compartment in the thermostatic head.

When setting a programme via the python script I wrote, you need to address each device by its RF address; when addressing devices via Openhab, you use the serial.  For example, a device might look like this (expressed as JSON):

```json
  {
    "rf_address": "150A88",
    "room_id": 2,
    "name": "Kitchen",
    "serial": "MET1821362",
    "battery": 0,
  }
```

To address it via Openhab configuration files, you need to create a [`thing`](https://www.openhab.org/docs/concepts/things.html) and one or more [`channel`](https://www.openhab.org/docs/concepts/things.html#channels)s. A `thing` plus `channel` is called an `item`, and `items` are how you build user interfaces and automatic rules.

Here's a single line of configuration:

```
Number   thermostat_kitchen_set_temp          "Set Temperature [%.1f °C]"     <Temperature>  (Thermostat,ThermostatSetter,GroundFloor)  {channel="max:thermostat:KET0436364:MET1821362:set_temp"}
```

This defines something called `thermostat_kitchen_set_temp`. It allows you to set the temperature of a thermostat.  The final part (`channel=..`) is the critical part. It says that the thing is a max thermostate, addressed at `KET0436364` (the Cube serial) `:MET1821362` (the thermostatic head serial), and we're interested in the `set_temp` channel.  Most of the other fields are related to how the thing wil be displayed on a screen. The part in brackets assigns the thing to three different Groups.

The boiler relay can be defined at its gpio pin, thus:
```
Switch boiler_switch "Boiler switch" <heating> (Basement) {gpio="pin:4 initialValue:low"}
```

The `items` format is described in full [here](https://www.openhab.org/docs/configuration/things.html#defining-things).

Once you have set up all your things (full example [here](https://github.com/sebbacon/home-automation/blob/master/examples/openhab2/items/heating.items)), you can set up rules.  Here's the rule for turning the boiler on and off:

```
rule "A valve changed - switch boiler"
when
    Member of Valves changed
then
    var allClosed = Valves.members.filter[ i | i.state == 0 ].size == Valves.members.size
    if(boiler_switch.state == ON && allClosed) {
       boiler_switch.sendCommand(OFF)
       logDebug("boiler", "Boiler turned off")
       }
    if(boiler_switch.state == OFF && !allClosed) {
       boiler_switch.sendCommand(ON)
       logDebug("boiler", "Boiler turned on")
      }
end
```

The full documentation for rules is [here](https://www.openhab.org/docs/configuration/rules-dsl.html). [My configuration](https://github.com/sebbacon/home-automation/tree/master/examples/openhab2/rules) also has a rule for a software switch to turn on "holiday mode" (every thermostat set to 14C), so I can flip it off when I'm leaving the house for a day or two.  There's also a rule to email me when any batteries are low.

Finally, you can set up a simple frontend (with switches, sliders, etc) using a `sitemap`.  The sitemap driving the phone screenshot above looks like this:

```
// https://docs.openhab.org/configuration/sitemaps.html#element-type-setpoint
sitemap default label="Heating"
{
    Switch item=holiday_switch hoplabel="Holiday mode"
    Switch item=boiler_switch label="Boiler"
    Switch item=networkdevice_sebphone_present label="Seb at home"
    Text item=wall_thermostat_get_temp label="Living space actual [%.1f °C]"
    Setpoint item=wall_thermostat_set_temp label="Living space target [%.1f °C]" step=1
    Group item=Batteries label="Low batteries [%d]"
    Group item=Valves label="Max valve position [%d%%]"
}
```

### Grafana

[This guide covers what you need to know](https://community.openhab.org/t/influxdb-grafana-persistence-and-graphing/13761)

It's a bit of a fiddle working out how to set up new graphs for the first time, but worth the hassle, as it allows you to fine-tune your programmes.


### Mobile phone

As well as installing the openhab client (which displays `sitemaps` configured as above), I've installed [Tasker](https://tasker.joaoapps.com/), as an experiment in automating things when I leave home.

Tasker is a very powerful and complex system for setting up rules for automating stuff on your phone. I've installed it because I something that detects my presence at home, so I can build up some rules for automatically turning on holiday mode.  Tasker can use proximity to specific mobile phone masts for this, which uses considerably less battery than GPS. When I'm near a given list of masts, I've set up Tasker to send an HTTP POST to the Openhab REST API to toggle a "Phone presence" switch.

If I decide it's accurate enough, the plan is to put it on my partner's phone too, and then when none of us is in, automatically pop up Openhab on my phone with a message asking if I want to turn on Vacation mode.

## Network

In order to access graphana and the openhab sitemap from my phone, I set up my router's firewall to forward direct to the Pi.  You'll save yourself some hassle if you forward between identical ports (e.g. `3333` on your router to `3333` on your Pi).

## Backups

It took a few days to get a system that I was happy with. It would be horrible to lose it all. Backups are important. [Here's some notes I made about backing up the system](https://github.com/sebbacon/home-automation/issues/3).

As well as a full disk image, I've got incremental backups of the configuration, including a JSON dump of the current programme state (created via [this script](), which [hasn't yet](https://github.com/hackercowboy/python-maxcube-api/pull/15) been merged into `max-cube-python`, so until it is you'll want to use [my fork](https://github.com/sebbacon/python-maxcube-api/tree/add-program-setting)).
