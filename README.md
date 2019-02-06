
# Digital Signage

## [Edge](Edge/README.md)

  * Camera interface
  * Face detection
      * face demographics classification
  * Simple ad server

### Run

    python3 Edge/signage.py &
    python3 Edge/ads.py


## [Cloud](Cloud/README.md)

  * Activity Monitoring Logic
      * Object tracking
  * Database for UI
  * UI
    * Flask Dashboard

### Run

    Cloud/SignageData/run.sh &
    python3 Cloud/SignageGUI/index.py &


# Releases

  * 1.0.1
    * video data collection
        * basic activity monitoring
        * age classification
        * gender classification
    * basic ad service
    * data API for secure web transfer
    * UI dashboard displays data

