# mPulse Annotator

This software will help you to add annotations to your Akamai mPulse dashboard. 
The content used for the annotations is based on the events generated on Akamai platform.

In more technical details mPulse Annotator leverages 
[Akamai Event Viewer API](https://developer.akamai.com/api/core_features/event_viewer/v1.html) 
and [mPulse Annotation API](https://developer.akamai.com/api/web_performance/mpulse_annotations/v1.html) 
to create the annotations in mPulse backend.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. 
See deployment for notes on how to deploy the project on a live system.

### Prerequisites

* Python v3.6 or higher
* Akamai OPEN Edgegrid for Python - [AkamaiOPEN-edgegrid-python](https://github.com/akamai/AkamaiOPEN-edgegrid-python)
* an Akamai OPEN Client API with a read access priviledge to Event Viewer API. 
* an Akamai mPulse tenant and user account that has API access enable

### Installing

Once project is downloaded and configured (see *Configuration* section below), there is no additional installation instruction needed.

### Docker

This project can be run within using a builtin Docker container image. The image is based on Alpine Linux, has a small footprint and comes with all required libraries.

This is how to build the Docker image:
```
docker build -t pmaugeri/ak-mpulse-annotator .
```

Assuming you have your events-selector.csv file in the local folder /root/events-selector.csv, you can then run a new container image that mounts your configuration file:
```
$ docker run --mount type=bind,source=/root/events-selector.csv,target=/root/ak-mpulse-annotator/events-selector.csv  -it pmaugeri/ak-mpulse-annotator
```

### Configuration

**File events-selector.csv**

Define the events you want to select for creating the annotations in the file events-selector.csv. This file is a 3-column CSV file with the following format:

```
<event definition ID>,<Event class name>,<filter criteria>
```

Example: you want to select activation of Property Manager configurations (Event Definition ID = 943951) for the configurations myconfig.domain.com and myotherconfig.domain.com: 

```
943951,PropertyManagerEvent,myconfig.domain.com;myotherconfig.domain.com
```

Example 2: you want to select purge by CP Code events (Event Definition ID = 229233) on CP Code 123456 and on CP Code 654321:

```
229233,FastPurgeEvent,123456;654321
```

Example 3: you may combine multiple event selectors:

```
943951,PropertyManagerEvent,myconfig.domain.com;myotherconfig.domain.com
229233,FastPurgeEvent,123456;654321
```


### Usage

You can invoke the mpulse-annotator with the following command line parameters:

* **-u:** the base URL (host for the Client API)
* **-c:** the client Token
* **-s:** the client secret
* **-o:** the access token
* **-t:** the starting time to retrieve events from
* **-a:** the mPulse API token
* **-m:** mPulse tenant name
* **-f:** path and file name to events selector file
* **-x:** this will prevent any annotation to be added to mPulse dashboard (simulation mode for testing purpose)

Example ('X' characters are hidden characters):

```
./mpulse-annotator.py -u akab-XXXX.luna.akamaiapis.net -c akab-XXXXX -s XXXXX -o akab-XXXXX-XXXXX -t 2018-12-1T08:00:00 -a XXXX-XXXX-XXXX-XXXX-XXXX -m "MPULSE TENANT" -f ./events-selector.csv
```

The appropriate date format can be automatically generated by using the following date commands:

* MacOS : `date -u -v -1H '+%Y-%m-%dT%H:%M:%S'`
* GNU/Linux : `date -d '1 hour ago' '+%Y-%m-%dT%H:%M:%S'`

This can be convenient if you run this using a scheduler such as `cron`.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
