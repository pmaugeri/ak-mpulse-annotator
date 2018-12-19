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

* Python v2.7.10 or higher
* Akamai OPEN Edgegrid for Python - [AkamaiOPEN-edgegrid-python](https://github.com/akamai/AkamaiOPEN-edgegrid-python)
* an Akamai OPEN Client API with a read access priviledge to Event Viewer API. 
* an Akamai mPulse tenant and user account that has API access enable

### Installing

Once project is downloaded and configured (see *Configuration* section below), there is no additional installation instruction needed.

### Configuration

**File .edgerc**

Save your Akamai OPEN Client API credentials in an **.edgerc** file located in the current working directory, following this format:

```
[edgercsection]
host = XXXX-XXXXXXX-XXXXXXX.luna.akamaiapis.net
client_token = XXXXXXX-XXXXXXX-XXXXXXX
client_secret = XXXXXXX
access_token = akab-XXXXXXX-XXXXXXX 
max-body = 131072
```

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

* **-s:** the section name in your .edgerc file
* **-t:** the starting time to retrieve events from
* **-a:** the mPulse API token
* **-m:** mPulse tenant name

Example:

```
./mpulse-annotator.py -s edgercsection -t 2018-12-1T08:00:00 -a XXXX-XXXX-XXXX-XXXX-XXXX -m "MPULSE TENANT"
```


## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
