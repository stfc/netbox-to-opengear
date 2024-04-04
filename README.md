# Netbox to Opengear configuration

This simple script pulls information from your serial console configuration in Netbox and puts it into your Opengear serial console, so you can use Netbox as your single source of truth.

See config.ini.example for example configuration.

Run `python3 opengear-netbox.py --console my-console-hostname.example.com` - make sure your console hostname matches in Netbox and is in DNS for this to work.
