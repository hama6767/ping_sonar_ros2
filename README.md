
## Overview

ROS 2 package for Blue Robotics Ping Sonar Altimeter and Echosounder
That's modified for U-CAT usage and it is folk from https://github.com/tasada038/ping_sonar_ros


### License

The source code is released under a [MIT license](LICENSE).

## Requirements
[Ping Sonar Altimeter and Echosounder](https://bluerobotics.com/store/sensors-sonars-cameras/sonar/ping-sonar-r2-rp/)

```
$ pip install --user bluerobotics-ping --upgrade
$ pip install pyserial
```


## Run
Publish sonar data
```
ros2 run ping_sonar_ros ping1d_node
```

## Ping sonar Topics
The topics of the ping_sonar_ros are as follows.

```
$ ros2 topic list
/ping1d/param/gain
/ping1d/param/interval
/ping1d/param/mode
/ping1d/param/speed
/ping1d/range
```

- std_msgs.msg Float32: /ping1d/param/gain
- std_msgs.msg Float32: /ping1d/param/interval
- std_msgs.msg Float32: /ping1d/param/mode
- std_msgs.msg Float32: /ping1d/param/speed
- sensor_msgs.msg Range: /ping1d/range

## Ping sonar Parameters
The parameters for the ping_sonar_ros are as follows.

```
$ ros2 param list
/ping1d_node:
  gain_num
  interval_num
  mode_auto
  scan_lenght
  scan_start
  speed
```

- gain_num parameter range is [0 - 6] (int).
- interval_num range is [50 - 200] (int, ms).
- mode_auto range is [0 or 1].
- scan_lenght range is [2000 - 10000] (int ms). Blue Robotics Inc. default is 2000 mm.
- scan_start range is [30 - 200]. Blue Robotics Inc. default is 100 mm.
- scan_start range is [1050000 - 1550000] (int mm/s).
