[![PayPal donate button](https://img.shields.io/badge/paypal-donate-yellow.svg)](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=E36NM78QVXA46 "Donate once-off to this project using Paypal")

#Welcome
This supporting add-on (SA) for Splunk enables lookup of *MAC* address field to IEEE registered vendor information; additional capabilities such as normalization of *MAC* address are also provided per Splunk Common Information model http://docs.splunk.com/Documentation/CIM/latest/User/NetworkTraffic. App comes with sample dashboards to showcase the dataset, however, it can be safely hidden without impacting functionality; details on hiding an app are described at http://docs.splunk.com/Documentation/Splunk/latest/AdvancedDev/ShareYourWork#Set_visibility

Mapping information is obtained from IEEE, found at http://standards.ieee.org/regauth/oui/oui.txt. Additional detail can be found at http://standards.ieee.org/faqs/regauth.html

This project is hosted on GitHub, see https://github.com/hire-vladimir/SA-mac_vendor

#Install
App installation is simple, and only needs to be present on the search head. Documentation around app installation can be found at http://docs.splunk.com/Documentation/AddOns/released/Overview/Singleserverinstall

#Getting Started
Lookup *mac_vendor_lookup* takes *mac* address an input argument; it performs a case insensitive "starts with" match on the *mac* field to determine vendor information. *mac* field is expected to be normalized per http://docs.splunk.com/Documentation/CIM/latest/User/NetworkTraffic, to help with this effort macro *normalize_mac_address* is provided.

```
The TCP/IP layer 2 Media Access Control (MAC) address of a packet's source/destination, such as 06:10:9f:eb:8f:14. Note: Always force lower case on this field. Note: Always use colons instead of dashes, spaces, or no separator.
```

**Note:** Lookup data is static, as in, it is refreshed every app release. It's possible to setup more frequent data refresh, by running the following:

`splunk cmd python SA-mac_vendor/bin/ieee_oui_parser.py > SA-mac_vendor/lookups/mac_vendor_lookup.csv`

## Screenshot
![mac address to vendor lookup for Splunk ](https://raw.githubusercontent.com/hire-vladimir/SA-mac_vendor/master/static/screenshot.png)

##System requirements
The app was tested on Splunk 6.2+ on CentOS Linux 7.1.

##Syntax
```... | `normalize_mac_address(mac)` | lookup mac_vendor_lookup mac OUTPUT mac_vendor, mac_vendor_address, mac_vendor_address2, mac_vendor_country | ...```

##Example
```| localop | stats count | fields - count | eval src_mac="cc-20-e8-01-ab-3f" | `normalize_mac_address(src_mac)` | lookup mac_vendor_lookup mac AS src_mac OUTPUT mac_vendor, mac_vendor_address, mac_vendor_address2, mac_vendor_country```

#Legal
* *Splunk* is a registered trademark of Splunk, Inc.
