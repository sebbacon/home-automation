#!/usr/bin/python3
"""This script is driven by dictionaries of per-room schedules.

The times are the times a temperature should *start*, e.g. `{"0650": 21}` means "turn it to 21C at 06:50".



"""
import argparse
import stat
import subprocess
import shutil
import tempfile
import os


devices = {
    "living room front": "OEQ1040676",
    "living room back": "OEQ1039575",
    "kitchen": "MEQ1821372",
    "study": "OEQ1039499",
    "wall thermometer": "OEQ1447059",
    "guest bedroom": "OEQ1039384",
    "beth bedroom": "OEQ1041021",
    "master bedroom": "OEQ1040288",
    "samuel bedroom": "OEQ1039491",
}
ON = True
OFF = False
# https://ref.homegear.eu/device.html?directory=MAX%21&file=BC-RT-TRX-CyG.xml&familyLink=max&name=BC-RT-TRX-CyG
# Went from 17 to 21 at 17:00
max_slots = 13
living_space_schedule = {
    "monday": {"0650": 21, "0900": 20, "1700": 21, "2230": OFF},
    "tuesday": {
        "0650": 21,
        "0900": 20,
        "1700": 21,
        "2140": OFF,
    },  # XXXX how does the TRV know the day and time?!
    "wednesday": {"0650": 21, "0900": 20, "1700": 21, "2230": OFF},
    "thursday": {"0650": 21, "090": 20, "1700": 21, "2230": OFF},
    "friday": {"0650": 21, "0900": 20, "1700": 21, "2230": OFF},
    "saturday": {"0650": 21, "0900": 20, "1700": 21, "2230": OFF},
    "sunday": {"0650": 21, "0900": 20, "1700": 21, "2230": OFF},
}

holiday_schedule = {
    "monday": {"1100": 8},
    "tuesday": {"1100": 8},
    "wednesday": {"1100": 8},
    "thursday": {"1100": 8},
    "saturday": {"1100": 8},
    "sunday": {"1100": 8},
}

guest_bedroom_schedule = {
    "monday": {"0650": 20, "0830": 18, "2030": 20, "2300": 18},
    "tuesday": {"0650": 20, "0830": 18, "2030": 20, "2300": 18},
    "wednesday": {"0650": 20, "0830": 18, "2030": 20, "2300": 18},
    "thursday": {"0650": 20, "0830": 18, "2030": 20, "2300": 18},
    "friday": {"0650": 20, "0830": 18, "2030": 20, "2300": 18},
    "saturday": {"0650": 20, "0830": 18, "2030": 20, "2300": 18},
    "sunday": {"0650": 20, "0830": 18, "2030": 20, "2300": 18},
}
holiday_schedules = {
    "wall thermometer": holiday_schedule,
    "living room front": holiday_schedule,
    "living room back": holiday_schedule,
    "kitchen": holiday_schedule,
    "guest bedroom": holiday_schedule,
    "beth bedroom": holiday_schedule,
    "samuel bedroom": holiday_schedule,
    "study": holiday_schedule,
    "master bedroom": holiday_schedule,
}

normal_schedules = {
    "wall thermometer": living_space_schedule,
    "living room front": living_space_schedule,
    "living room back": living_space_schedule,
    "kitchen": living_space_schedule,
    "guest bedroom": holiday_schedule,
    "master bedroom": {
        "monday": {"0650": 18, "0900": 21, "1600": 18, "2230": 16},
        "tuesday": {"0650": 18, "0900": 21, "2000": 18, "2230": 16},
        "wednesday": {"0650": 18, "0900": 21, "1600": 18, "2230": 16},
        "thursday": {"0650": 18, "0900": 21, "1600": 18, "2230": 16},
        "friday": {"0650": 18, "0900": 21, "1600": 18, "2230": 16},
        "saturday": {"0650": 19, "0830": 16, "2130": 18, "2300": 16},
        "saturday": {"0650": 19, "0830": 16, "2130": 18, "2300": 16},
    },
    "beth bedroom": {
        "monday": {"0650": 18, "0830": OFF, "1500": 18, "2030": 16},
        "tuesday": {"0650": 18, "0830": OFF, "1500": 18, "2030": 16},
        "wednesday": {"0650": 18, "0830": OFF, "1500": 18, "2030": 16},
        "thursday": {"0650": 18, "0830": OFF, "1500": 18, "2030": 16},
        "friday": {"0650": 18, "0830": OFF, "1500": 18, "2030": 16},
        "saturday": {"0650": 18, "0830": 16, "1800": 18, "2030": 16},
        "sunday": {"0650": 18, "0830": 16, "1800": 18, "2030": 16},
    },
    "samuel bedroom": {
        "monday": {"0650": 18, "0830": OFF, "1500": 18, "2030": 16},
        "tuesday": {"0650": 18, "0830": OFF, "1500": 18, "2030": 16},
        "wednesday": {"0650": 18, "0830": OFF, "1500": 18, "2030": 16},
        "thursday": {"0650": 18, "0830": OFF, "1500": 18, "2030": 16},
        "friday": {"0650": 18, "0830": OFF, "1500": 18, "2030": 16},
        "saturday": {"0650": 18, "0830": 16, "1800": 18, "2030": 16},
        "sunday": {"0650": 18, "0830": 16, "1800": 18, "2030": 16},
    },
    "study": {
        "monday": {"0715": 21, "1600": OFF},
        "tuesday": {"0715": 21, "1600": OFF},
        "wednesday": {"0715": 21, "1600": OFF},
        "thursday": {"0715": 21, "1600": OFF},
        "friday": {"0715": 21, "1600": OFF},
        "saturday": {"0650": OFF},
        "sunday": {"0650": OFF},
    },
}
guest_schedules = normal_schedules.copy()
guest_schedules["guest bedroom"] = guest_bedroom_schedule


def time_to_mins(time):
    hours = int(time[:2])
    mins = int(time[2:])
    return hours * 60 + mins


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--schedule", type=str, choices=["guest", "normal", "holiday"], required=True
    )
    args = parser.parse_args()
    if args.schedule == "normal":
        schedules = normal_schedules
    elif args.schedule == "guest":
        schedules = guest_schedules
    else:
        schedules = holiday_schedules

    instructions = []
    # homegear -e 'rc print_r($hg->putParamset(4, 0, array("ENDTIME_WEDNESDAY_1" => 1200, "TEMPERATURE_WEDNESDAY_1" => 32)));'
    # XXX I'm not sure what happens when I set the holiday schedule. In the evening, while the prog obviously changes, the temp does not change to 11.
    # Either you need to overwrite all the other slots with something
    # Or....?
    for device, device_code in devices.items():
        schedule = schedules[device]
        instructions.append(f"$peerId = $hg->getPeerId(1, '{device_code}')[0];")
        instructions.append(f"$hg->setValue('{device_code}:1', 'AUTO_MODE', true);")
        settings_instructions = []
        i = 1
        for day, times in schedule.items():
            for i, (t, temp) in enumerate(times.items(), start=1):
                t = time_to_mins(t)
                settings_instructions.append(f"'ENDTIME_{day.upper()}_{i}' => {t}")
                # Because this is the *end* time of the *previous* temperature
                temp = list(times.values())[i - 2] or 5
                settings_instructions.append(
                    f"'TEMPERATURE_{day.upper()}_{i}' => {temp}"
                )
        while i < 13:
            i += 1
            # Overwrite the rest of the temp slots with the last value
            settings_instructions.append(f"'ENDTIME_{day.upper()}_{i}' => {t}")
            settings_instructions.append(f"'TEMPERATURE_{day.upper()}_{i}' => {temp}")
        instructions.append(
            f"$hg->putParamset($peerId, 0, array({', '.join(settings_instructions)}));"
        )

    template = """
    <?php
    $hg = new \Homegear\Homegear();
    {}
    ?>"""

    target_file = "/var/lib/homegear/scripts/Prog.php"
    with tempfile.NamedTemporaryFile(mode="w") as f:
        f.write(template.format("\n".join(instructions)))
        f.flush()
        shutil.copy(f.name, target_file)
        os.chmod(target_file, 0o775)
        subprocess.check_call("homegear -e runscript Prog.php", shell=True)


if __name__ == "__main__":
    main()
