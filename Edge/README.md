# Signage Edge Processing

## Deployment

  * `client.py` is the configurable python client.
  * `singlerun.sh` runs the client with set configuration.

### Configuration
Configuration is located in `Signage/singlerun.sh`:

  * address for IP camera
  * address for application server
  * name for the location
  * name for the camera

Set up `/etc/network/interfaces` to allow access to necessary IP cameras.

### Automation
 
Add this to `/etc/rc.local`:

    printf "Starting signage script.\n"
    runuser -l pi -c "screen -dmS signage"
    runuser -l pi -c "screen -S signage -p 0 -X stuff 'watch -n 1 /home/pi/Signage/singlerun.sh\n'"

  * `singlerun.sh` is our main script
  * `watch` re-runs the script when it see the script complete.
  * `/etc/rc.local` creates a screen session for `watch` on system startup.