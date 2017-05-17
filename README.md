# Snuk-io Challenge

This repo contains the solution for the Snuk.io distributed systems challenge. The purpose of the challenge is to create a prototype for a simple heating control device.

Conditions of operation:
- 1 single room
- multiple temperature sensors
- 1 radiator valve (actuator)

The key point is to maintain the temperature of the room at 22C by setting the valve openness from 0 (fully closed) to 100 (fully open).

The technology behind this control system involves a MQTT brocker and the python paho-mqtt library.

 ### Usage

* run mqtt brocker with docker:
   ```
    docker run -it -p 1883:1883 --name=mosquitto  toke/mosquitto
    ```
* install python 3
* install the following python modules:
    * numpy
    * paho-mqtt
* execute the main python script file:
    ```
    python main.py
    ```

### Solution

The implementation involves two main actors:

* **publishers**: represent nodes that send temperature to MQTT brocker witht he following format.

topic: /readings/temperature

```
{
  "sensorID": "sensor-1",
  "type": "temperature",
  "value": 25.3
}
```

The number of temperature sensors in the room can be modified with the variable **numNodes**.
The interval at which the sensors send the data to the brocker can be modified with the variable **interval**

There are 2 ways of generating temperature data :

genTempCase = 0 generates uniform data with a specified interval (**minRange** and  **maxRange**)
genTempCase = 1 generates random temp values within a given interval (**minRange** and  **maxRange**)

* **subscriber**: receives message from the temperature publisher, performs several calculations, and publishes a message to control the valve.

topic: /actuators/room-1
```
{
  "level": 14
}
```

The **suscriber** parses all data received through the **/readings/temperature** topic and waits for all the sensors to report in order to calculate the average temperature of the room.

In order to avoid changing the openess/closeness of the valve all time and control the time in which the valve operates, several samples are saved in a temperature array.
 For example, if interval time is 10 seconds and sample is set to ten, actuator will only change temperature every 100 seconds. **

 After all samples are collected, the code applies a simple fuzzy logic control with 3 ranges:

 * If current temperature is **above** threshold, close the valve 0%. (fast movement)
 * If current temperature is **below** threshold, open the valve 100%. (fast movement)
 * If current temperature is in between +- middleRangeInterval, keep valve close for a certain amount of time.
 For example: setPoint = 22 and interval = 0.5. If current temperature is between 21.5 and 22.5, decrease valve firing period
* If current temperature interval is in between max/min threshold and middleRange threshold, apply a proportion (%) of openess.

 ### Additional information

* A simple fuzzy logic control was used due to time constraint, however, the best idea would be to implement a PID controller with corrent PID tunings.

* It would be best to implement another way of simulating temperature, probably defining test cases for increasing and decreasing temperature uniformly.

 ### Next Steps

The things to to next prior to this prototype would be:

* code a more efficient way of simulating temperature sensors
* add some test cases to simulate several temperature behaviours
* change fuzzy logic control to PID control
* Wrap subscriber and publisher code in a class and creat a json file for controlling interval settings (OOP)
