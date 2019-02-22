
import config

###########################################################
#####                  Configuration                  #####
#####        Used by signage and ad services          #####
###########################################################

cfg_defaults = { 
      'logging'               : {
          'logfile_path'      : None
        , 'logfile_maxbytes'  : 3750000
        , 'log_level'         : 'info'
    }
 
    , 'camera'                : {
          'enabled'           : False
        , 'stream_address'    : '192.168.1.168/usecondstream'
        , 'protocol'          : 'rtsp://'
        , 'location_name'     : 'signage-analysis-demo'
        , 'name'              : 'signage-camera-1'
        , 'credentials'       : '*user*:*pass*'
        , 'rotation'          : 0
        , 'p_fov'             : 78.0
        , 'p_fcl'             : 336.6
    }

    , 'demographics'          : {
          'enabled'           : False
        , 'model_path'        : '/opt/signage/models/wide_resnet_age_gender.h5'
    }

    , 'tracking'              : {
          'iou_threshold'     : 0.8
        , 'min_secs_live'     : 2 
    }

    , 'data'                  : {
          'enabled'           : False
        , 'credentials'       : '*user*:*pass*'
        , 'data_server'       : '127.0.0.1:5000'
        , 'data_protocol'     : 'http://'
    }
    
    , 'ads'                   : {
          'enabled'           : False
        , 'server'            : ['localhost',18861]
        , 'library'           : '/opt/signage/videos'
        , 'logfile_path'      : None
        , 'logfile_maxbytes'  : 3750000
        , 'log_level'         : 'info'
        , 'cooldown_secs'     : 5
        , 'allow_repeats'     : False
        , 'display'           : {
              'rotation'          : 0
            , 'window'            : [0,0,480,640]
            , 'debug_view'        : False
            }
    }
    }

cfg = config.Config(
      filepath = "/boot/signage/config.yml"
    , description = "Orchestration and Image Feed"
    , defaults_dict = cfg_defaults
    , maskedpath = "/opt/signage/credentials.yml")

cfg.mask('data.credentials'   ,'*user*:*pass*')
cfg.mask('camera.credentials' ,'*user*:*pass*')
