import time

from rclpy.node import Node
from sensor_msgs.msg import Range
from std_msgs.msg import Float32

from rcl_interfaces.msg import SetParametersResult

from brping import Ping1D
#import importlib
#module_name = "ping_sonar_ros.ping-python.brping.ping1d"
#module = importlib.import_module(module_name)


class Ping1dComponent(Node):
  def __init__(self):
    super().__init__("ping1d_node")
    self.publisher_ = self.create_publisher(Range, "/ping1d/range", 10)
    self.dist_pub_ = self.create_publisher(Float32, "/ping1d/distance", 10)
    self.confidence_pub_ = self.create_publisher(Float32, "/ping1d/confidence", 10)
    self.speed_pub_ = self.create_publisher(Float32, "/ping1d/param/speed", 10)
    self.interval_pub_ = self.create_publisher(Float32, "/ping1d/param/interval", 10)
    self.gain_pub_ = self.create_publisher(Float32, "/ping1d/param/gain", 10)
    self.mode_pub_ = self.create_publisher(Float32, "/ping1d/param/mode", 10)
    self.timer_ = self.create_timer(0.1, self.range_callback)

    ### Declare ROS 2 Parameter
    self.declare_parameter('speed', 1450000)  # 1550000 mm/s 1550 m/s
    self.speed_:float = self.get_parameter('speed').value
    self.declare_parameter('interval_num', 100)
    self.interval_num_:float = self.get_parameter('interval_num').value
    self.declare_parameter('gain_num', 2) # int 0 - 6
    self.gain_num_:int = self.get_parameter('gain_num').value
    self.declare_parameter('scan_start', 100) # default 100 [mm] range(30 to 200)
    self.scan_start_:float = self.get_parameter('scan_start').value
    self.declare_parameter('scan_lenght', 3000) # default 2000 [mm] range(2000 to 10000)
    self.scan_lenght_:float = self.get_parameter('scan_lenght').value
    self.declare_parameter('mode_auto', 0) # default 0: manual mode, 1: auto mode
    self.mode_auto_:int = self.get_parameter('mode_auto').value

    self.param_handler_ptr_ = self.add_on_set_parameters_callback(self.set_param_callback)

    self.init_ping()
    while self.ping.initialize() is False:
        if self.ping.initialize() is False:
          print("Failed to initialize Ping!")
          self.init_ping()
          time.sleep(1)

    print("connection success")
    ### Set Initial parameter
    # self.id = self.ping.get_device_id()
    self.ping.set_speed_of_sound(self.speed_)
    self.ping.set_ping_interval(self.interval_num_)
    self.ping.set_gain_setting(self.gain_num_)
    self.ping.set_range(self.scan_start_, self.scan_lenght_)
    self.ping.set_mode_auto(self.mode_auto_)

  def init_ping(self):
    ### Make a new Ping
    self.port = "/dev/ttyUSBping"
    self.baudrate = 115200
    self.ping = Ping1D()
    self.ping.connect_serial(self.port, self.baudrate)


  def range_callback(self):
    # distance: Units: mm; The current return distance determined for the most recent acoustic measurement.\n
    # confidence: Units: %; Confidence in the most recent range measurement.\n
    # transmit_duration: Units: us; The acoustic pulse length during acoustic transmission/activation.\n
    # ping_number: The pulse/measurement count since boot.\n
    # scan_start: Units: mm; The beginning of the scan region in mm from the transducer.\n
    # scan_length: Units: mm; The length of the scan region.\n
    # gain_setting: The current gain setting. 0: 0.6, 1: 1.8, 2: 5.5, 3: 12.9, 4: 30.2, 5: 66.1, 6: 144\n
    ### Comment or Uncomment below
    # data = self.ping.get_distance()
    # print("data:%d\n", data)

    # distance: Units: mm; Distance to the target.\n
    # confidence: Units: %; Confidence in the distance measurement.\n
    simple_data = self.ping.get_distance()
    # print("simple data:%d\n", simple_data)

    # scan_start: Units: mm; The beginning of the scan range in mm from the transducer.\n
    # scan_length: Units: mm; The length of the scan range.\n
    range_data = self.ping.get_range()
    # print("scan_start: %s\tscan_length: %s " % (range_data["scan_start"], range_data["scan_length"]))

    # gain_setting: The current gain setting. 0: 0.6, 1: 1.8, 2: 5.5, 3: 12.9, 4: 30.2, 5: 66.1, 6: 144\n
    gain = self.ping.get_gain_setting()
    # print("gain:%d\n", gain)

    # speed_of_sound: Units: mm/s; The speed of sound in the measurement medium. ~1,500,000 mm/s for water.\n
    speed_sound = self.ping.get_speed_of_sound()
    # print("speed_of_sound: %s\n" % (speed_sound["speed_of_sound"])) 

    # firmware_version_major: Firmware major version.\n
    # firmware_version_minor: Firmware minor version.\n
    # voltage_5: Units: mV; Device supply voltage.\n
    # ping_interval: Units: ms; The interval between acoustic measurements.\n
    # gain_setting: The current gain setting. 0: 0.6, 1: 1.8, 2: 5.5, 3: 12.9, 4: 30.2, 5: 66.1, 6: 144\n
    # mode_auto: The current operating mode of the device. 0: manual mode, 1: auto mode\n
    ### Comment or Uncomment below
    # general = self.ping.get_general_info()
    # print("general:%d\n", general)

    # ping_interval: Units: ms; The minimum interval between acoustic measurements. The actual interval may be longer.\n
    interval = self.ping.get_ping_interval()
    # print("interval:%d\n", interval)

    mode_auto = self.ping.get_mode_auto()
    # print("mode_auto:%d\n", mode_auto)
 

    ### ROS 2 data publisher
    range_msg = Range()
    range_msg.header.stamp = self.get_clock().now().to_msg()
    range_msg.header.frame_id = "range_link"
    range_msg.radiation_type = Range.ULTRASOUND
    range_msg.field_of_view = 0.1 # [rad]
    range_msg.min_range = float(range_data["scan_start"]/1000) # [m]
    range_msg.max_range = float(range_data["scan_length"]/1000) # [m]
    range_msg.range = float(simple_data["distance"]/1000) # [m]
    self.publisher_.publish(range_msg)

    dist_msg = Float32()
    conf_msg = Float32()
    speed_msg = Float32()
    interval_msg = Float32()
    gain_msg = Float32()
    mode_msg = Float32()
    dist_msg.data = float(simple_data["distance"]/1000)
    conf_msg.data = float(simple_data["confidence"])
    speed_msg.data = float(speed_sound["speed_of_sound"]/1000)
    interval_msg.data = float(interval["ping_interval"])
    gain_msg.data = float(gain["gain_setting"])
    mode_msg.data = float(mode_auto["mode_auto"])
    self.dist_pub_.publish(dist_msg)
    self.speed_pub_.publish(speed_msg)
    self.interval_pub_.publish(interval_msg)
    self.gain_pub_.publish(gain_msg)
    self.mode_pub_.publish(mode_msg)
    #self.get_logger().info("Distance: {}".format(range_msg.range))
    #self.get_logger().info("Confidence: {}".format(conf_msg.data))

  def set_param_callback(self, params):
        result = SetParametersResult(successful=True)
        for param in params:
            if param.name == 'speed':
                self.speed_ = param.value
                self.get_logger().info('Updated speed value: %f' % self.speed_)
                self.ping.set_speed_of_sound(self.speed_)
            if param.name == 'interval_num':
                self.interval_num_ = param.value
                self.get_logger().info('Updated interval_num value: %f' % self.interval_num_)
                self.ping.set_ping_interval(self.interval_num_)
            if param.name == 'gain_num':
                self.gain_num_ = param.value
                self.get_logger().info('Updated gain_num value: %f' % self.gain_num_)
                self.ping.set_gain_setting(self.gain_num_)
            if param.name == 'scan_start':
                self.scan_start_ = param.value
                self.get_logger().info('Updated scan_start value: %f' % self.scan_start_)
                self.ping.set_range(self.scan_start_, self.scan_lenght_)
            if param.name == 'scan_lenght':
                self.scan_lenght_ = param.value
                self.get_logger().info('Updated scan_lenght value: %f' % self.scan_lenght_)
                self.ping.set_range(self.scan_start_, self.scan_lenght_)
            if param.name == 'mode_auto':
                self.mode_auto_ = param.value
                self.get_logger().info('Updated mode_auto value: %f' % self.mode_auto_)
                self.ping.set_mode_auto(self.mode_auto_)
        return result
