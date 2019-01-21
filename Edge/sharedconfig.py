
import config

###########################################################
##############         Configuration         ##############
###########################################################

cfg_defaults = { 
      'camera'                : {
          'enabled'           : False
        , 'stream_address'    : '192.168.1.168/usecondstream'
        , 'protocol'          : 'rtsp://'
        , 'location_name'     : 'signage-analysis-demo'
        , 'name'              : 'signage-camera-1'
        , 'credentials'       : '*user*:*pass*'
        , 'rotation'          : 0
    }
    
    , 'logging'               : {
          'enabled'           : True
        , 'logfile_path'      : 'signage.log'
        , 'logfile_maxbytes'  : 3750000
    }
 
    , 'ads'                   : {
          'enabled'           : False
        , 'server'            : ['localhost',18861]
        , 'library'           : '/opt/signage/videos'
        , 'pause_secs'        : 5
        , 'display'           : {
              'rotation'          : 0
            , 'window'            : [400,0,400,480]
            , 'debug_view'        : False
            }
    }

    , 'data'                  : {
          'enabled'           : False
        , 'credentials'       : '*user*:*pass*'
        , 'data_server'       : '127.0.0.1:5000'
        , 'data_protocol'     : 'http://'
    }

    , 'demographics'          : {
          'enabled'           : False
    }
    }

cfg = config.Config(
      filepath = "/boot/signage/config.yml"
    , description = "Orchestration and Image Feed"
    , dictionary = cfg_defaults
    , maskedpath = "/opt/signage/credentials.yml")

cfg.mask('data.credentials'   ,'*user*:*pass*')
cfg.mask('camera.credentials' ,'*user*:*pass*')
