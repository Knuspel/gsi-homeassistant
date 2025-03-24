# Simple Integration for Grünstromindex.de

This Integration creates six sensors that expose the metrics from Grünstromindex.de to Homeassistant.
It creates the following Sensors:

* ```CO2AverageSensor``` Showing the CO2 Equivilant average outpu for the current Day or Period
* ```CO2StandardSensor``` Showing the CO2 Equivilant standard electricity output for the current Day or Period
* ```CO2OekostromSensor``` Showing the CO2 Equivilant green electricity output for the current Day or Period
* ```GSISensor``` Showing the GSI Factor in percent. Basically how green is electricity right now.
* ```WindPowerSensor``` Showing the Wind Power Percentage in the current power mix.
* ```SolarPowerSensor``` Showing the Solar Power Percentage in the current power mix.

It can be set up with just the German Postleitzahl / Zipcode but you might run into API Limits.
Optionally you can input an API key, that you can optain from here: https://console.corrently.io/
