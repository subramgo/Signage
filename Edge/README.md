# Signage project for retail

## To-Do

  1. OpenCV is still caching frames in a way leading to delay

## Deployment

  * run.sh uses `watch` to keep the script running
  * singlerun.sh runs the script with set configuration
  * client.py is the configurable python client.

### `screen` and `rc.local`

Add this to `/etc/rc.local`:

    printf "Starting signage script.\n"
    runuser -l pi -c "screen -dmS signage"
    runuser -l pi -c "screen -S signage -p 0 -X stuff 'watch -n 1 /home/pi/Signage/singlerun.sh\n'"

## Configuration
Configuration is located in `Signage/singlerun.sh`:

  * address for IP camera
  * address for application server
  * name for this location
  * name for this camera


