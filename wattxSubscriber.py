import json
import paho.mqtt.client as mqtt


tempArr = [None] * 3 # array for saving multiple sensor averages
average = ""
setPoint = 22 # desired temperature
tempControlArr = [] # variable for saving multiple temperature samples
sampingInterval = 3 # default interval factor before activating valve

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, rc):
    print("Connected with result code "+str(rc))
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("/readings/temperature")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(str(msg.payload))
    calculateAverage(client,msg.payload)

def calculateAverage(client, message):

    """ Parse temperature JSON and calculate average for overall room temperature
    """

    if not any(v is None for v in tempArr): #if we have gathered all data from sensors in the room
        average = sum(tempArr) / len(tempArr) # calculate average temp of room
        tempControl(client, average) # apply control to valve
        for i in range(0,len(tempArr)):
            tempArr[i] = None # empty temperature array

    data = json.loads(message)
    sensorNumber = data["sensorID"].split("-")
    tempArr[ int(sensorNumber[1]) ] = int(data["value"]) # fill array depending on sensor id received

def tempControl(client, currTemperature):

    """ simple fuzzy logic with 4 ranges
    (valve 100%) minThreshold <----- +- 2 | setPoint (50%) +- 2 | -----> maxThreshold (valve 0%)
    """

    global sampingInterval
    global setPoint
    data = {}
    maxThreshold = setPoint + 5 # max temp threshold
    minThreshold = setPoint - 5 # min temp threshold
    maxMidRangeTh = setPoint + 1 # middle max temp threshold
    minMidRangeTh = setPoint - 1 # middle min temp threshold

    # save all temperatures up to the samplingInterval
    # Example: if temp sensor interval = 10 seconds and sampling interval = 10..
    #  Actuator will change interval * sampling interval = 100 seconds
    if(len(tempControlArr) != sampingInterval):
        tempControlArr.append(currTemperature)

    else:
        currTemperature = sum(tempControlArr) / len(tempControlArr)
        print(currTemperature)
        del tempControlArr[:]

        if(currTemperature >= maxThreshold): # temperature is above threshold, close the valve 0%. (fast movement)
            data['level'] = 0
        elif(currTemperature <= minThreshold): # temperature is below threshold, close the valve 100%. (fast movement)
            data['level'] = 100
        elif( currTemperature >= minMidRangeTh and currTemperature <= maxMidRangeTh ): # temperature is near set point
            data['level'] = 0 # keep valve close for x time defined by sampling Interval.
            sampingInterval = 10 # make actuator to rest more time
        else:
            response = int(round( (currTemperature * 50)/setPoint )) # get a percentage of openess
            sampingInterval = 5
            data['level'] = response

        print(json.dumps(data))
        client.publish("/actuators/room-1", json.dumps(data)) # publish data to mqtt
