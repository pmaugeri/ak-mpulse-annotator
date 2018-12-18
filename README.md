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

**Software**

* Python v2.7.10 or higher
* Akamai OPEN Edgegrid for Python - [AkamaiOPEN-edgegrid-python](https://github.com/akamai/AkamaiOPEN-edgegrid-python)

**Configuration**

* an Akamai OPEN Client API with a read access priviledge to Event Viewer API. 
These credentials should be defined in an **.edgerc** file located in the current working directory, and following this format:

```
[edgercsection]
host = XXXX-XXXXXXX-XXXXXXX.luna.akamaiapis.net
client_token = XXXXXXX-XXXXXXX-XXXXXXX
client_secret = XXXXXXX
access_token = akab-XXXXXXX-XXXXXXX 
max-body = 131072
```

* an Akamai mPulse tenant and user account that has API access enable

### Installing

No specific installing instructions for this project apart from the creation of the .edgerc file.


## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE) file for details

## Authors

[...]

## Acknowledgments

[...]
