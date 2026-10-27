#!/usr/bin/env bash
for k in AutomountEnabled AutomountOnLogin AutomountOnPlugin; do
    [[ $(kreadconfig6 --file kded_device_automounterrc --group General --key "$k") == true ]] || exit 1
done
