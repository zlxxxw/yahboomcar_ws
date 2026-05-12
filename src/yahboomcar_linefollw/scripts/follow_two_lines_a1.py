#!/usr/bin/env python2
# encoding: utf-8
import os
import threading
import math
import rospkg
import numpy as np
import cv2 as cv
from follow_common import *
from std_msgs.msg import Bool
from geometry_msgs.msg import Twist
from dynamic_reconfigure.server import Server
from dynamic_reconfigure.client import Client
from sensor_msgs.msg import CompressedImage, LaserScan, Image
from yahboomcar_linefollw.cfg import LineDetectPIDConfig

RAD2DEG = 180 / math.pi


class TwoLineCenterFollower:
    def __init__(self):
        rospy.on_shutdown(self.cancel)
        rospy.init_node("TwoLineCenterFollower", anonymous=False)

        # 状态与参数
        self.img = None
        self.hsv_range = ()
        self.Roi_init = ()
        self.select_flags = False
        self.Track_state = 'identify'  # init / identify / tracking / mouse
        self.windows_name = 'frame'

        # 运行时标志
        self.Start_state = True
        self.dyn_update = False
        self.warning = 0
        self.cols, self.rows = 0, 0
        self.Mouse_XY = (0, 0)

        # 运行配置
        self.img_flip = rospy.get_param("~img_flip", False)
        self.VideoSwitch = rospy.get_param("~VideoSwitch", False)
        self.show_gui = rospy.get_param("~show_gui", False)
        self.hsv_text = rospkg.RosPack().get_path("yahboomcar_linefollw")+"/scripts/LineFollowHSV.text"

        # 控制与动态参数
        self.ros_ctrl = ROSCtrl()
        Server(LineDetectPIDConfig, self.dynamic_reconfigure_callback)
        self.dyn_client = Client("TwoLineCenterFollower", timeout=60)
        self.scale = 1000
        self.FollowLinePID = (60, 0, 20)
        self.linear = 0.2
        self.LaserAngle = 30
        self.ResponseDist = 0.00
        self.PID_init()

        # 订阅/发布
        self.sub_scan = rospy.Subscriber('/scan', LaserScan, self.registerScan, queue_size=1)
        self.pub_rgb = rospy.Publisher("/linefollw/rgb", Image, queue_size=1)
        self.pub_Buzzer = rospy.Publisher('/Buzzer', Bool, queue_size=1)
        if self.VideoSwitch == False:
            from cv_bridge import CvBridge
            self.bridge = CvBridge()
            self.sub_img = rospy.Subscriber("/usb_cam/image_raw/compressed", CompressedImage, self.compressed_callback, queue_size=1)

    def cancel(self):
        self.Reset()
        self.ros_ctrl.cancel()
        self.sub_scan.unregister()
        if self.VideoSwitch == False:
            self.sub_img.unregister()
            cv.destroyAllWindows()
        self.pub_rgb.unregister()
        self.pub_Buzzer.unregister()
        rospy.loginfo("Shutting down TwoLineCenterFollower node.")

    def compressed_callback(self, msg):
        if not isinstance(msg, CompressedImage):
            return
        start = time.time()
        frame = self.bridge.compressed_imgmsg_to_cv2(msg, "bgr8")
        action = (cv.waitKey(1) & 0xFF) if self.show_gui else 255
        rgb_img, binary = self.process(frame, action)
        end = time.time()
        fps = 1 / max(1e-6, (end - start))
        text = "FPS : " + str(int(fps))
        cv.putText(rgb_img, text, (30, 30), cv.FONT_HERSHEY_SIMPLEX, 0.6, (100, 200, 200), 1)
        if len(binary) != 0:
            out_img = ManyImgs(1, ([rgb_img, binary]))
            self.pub_rgb.publish(self.bridge.cv2_to_imgmsg(out_img , "bgr8"))
            if self.show_gui:
                cv.imshow(self.windows_name, out_img)
        else:
            self.pub_rgb.publish(self.bridge.cv2_to_imgmsg(rgb_img, "bgr8"))
            if self.show_gui:
                cv.imshow(self.windows_name, rgb_img)

    def process(self, rgb_img, action):
        binary = []
        rgb_img = cv.resize(rgb_img, (640, 480))
        if self.img_flip is True:
            rgb_img = cv.flip(rgb_img, 1)

        if action == 32:
            self.Track_state = 'tracking'
        elif action == ord('i') or action == 105:
            self.Track_state = "identify"
        elif action == ord('r') or action == 114:
            self.Reset()
        elif action == ord('q') or action == 113:
            self.cancel()

        if self.Track_state == 'init':
            if self.show_gui:
                cv.namedWindow(self.windows_name, cv.WINDOW_AUTOSIZE)
                cv.setMouseCallback(self.windows_name, self.onMouse, 0)
                if self.select_flags is True:
                    cv.line(rgb_img, self.cols, self.rows, (255, 0, 0), 2)
                    cv.rectangle(rgb_img, self.cols, self.rows, (0, 255, 0), 2)
                    if self.Roi_init[0] != self.Roi_init[2] and self.Roi_init[1] != self.Roi_init[3]:
                        rgb_img, self.hsv_range = self.roi_to_hsv(rgb_img, self.Roi_init)
                        self.dyn_update = True
                    else:
                        self.Track_state = 'init'
            else:
                # 无GUI模式下无法交互选ROI，退回到 identify 读取文件HSV
                self.Track_state = 'identify'
        elif self.Track_state == "identify":
            if os.path.exists(self.hsv_text):
                self.hsv_range = read_HSV(self.hsv_text)
            else:
                self.Track_state = 'init'

        if self.Track_state != 'init' and len(self.hsv_range) != 0:
            rgb_img, binary, center_x = self.detect_two_lines_and_center(rgb_img, self.hsv_range)
            if self.dyn_update is True:
                write_HSV(self.hsv_text, self.hsv_range)
                params = {'Hmin': self.hsv_range[0][0], 'Hmax': self.hsv_range[1][0],
                          'Smin': self.hsv_range[0][1], 'Smax': self.hsv_range[1][1],
                          'Vmin': self.hsv_range[0][2], 'Vmax': self.hsv_range[1][2]}
                try:
                    self.dyn_client.update_configuration(params)
                except Exception:
                    pass
                self.dyn_update = False
        else:
            center_x = None

        if self.Track_state == 'tracking':
            if center_x is not None:
                threading.Thread(target=self.execute, args=(center_x,)).start()
        else:
            if self.Start_state is True:
                self.ros_ctrl.pub_cmdVel.publish(Twist())
                self.Start_state = False
        return rgb_img, binary if isinstance(binary, np.ndarray) else []

    def onMouse(self, event, x, y, flags, param):
        if event == 1:
            self.Track_state = 'init'
            self.select_flags = True
            self.Mouse_XY = (x, y)
        if event == 4:
            self.select_flags = False
            self.Track_state = 'mouse'
        if self.select_flags is True:
            self.cols = min(self.Mouse_XY[0], x), min(self.Mouse_XY[1], y)
            self.rows = max(self.Mouse_XY[0], x), max(self.Mouse_XY[1], y)
            self.Roi_init = (self.cols[0], self.cols[1], self.rows[0], self.rows[1])

    def roi_to_hsv(self, img, Roi):
        img, hsv_range = color_follow().Roi_hsv(img, Roi)
        return img, hsv_range

    def detect_two_lines_and_center(self, rgb_img, hsv_msg):
        # 截取下半部分，避免天空/墙等干扰
        height, width = rgb_img.shape[:2]
        img = rgb_img.copy()
        img[0:int(height / 2), 0:width] = 0

        hsv_img = cv.cvtColor(img, cv.COLOR_BGR2HSV)
        lower = np.array(hsv_msg[0], dtype="uint8")
        upper = np.array(hsv_msg[1], dtype="uint8")
        mask = cv.inRange(hsv_img, lower, upper)
        color_mask = cv.bitwise_and(hsv_img, hsv_img, mask=mask)
        gray_img = cv.cvtColor(color_mask, cv.COLOR_RGB2GRAY)

        kernel = cv.getStructuringElement(cv.MORPH_RECT, (5, 5))
        gray_img = cv.morphologyEx(gray_img, cv.MORPH_CLOSE, kernel)
        _, binary = cv.threshold(gray_img, 10, 255, cv.THRESH_BINARY)

        find_contours = cv.findContours(binary, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
        contours = find_contours[1] if len(find_contours) == 3 else find_contours[0]

        center_x = None
        if len(contours) >= 2:
            areas = [cv.contourArea(c) for c in contours]
            idx = np.argsort(areas)[-2:]
            c1, c2 = contours[idx[0]], contours[idx[1]]
            x1 = int(cv.moments(c1)['m10'] / max(1.0, cv.moments(c1)['m00']))
            x2 = int(cv.moments(c2)['m10'] / max(1.0, cv.moments(c2)['m00']))
            # 在图像上可视化两条线的质心
            cv.circle(rgb_img, (x1, height - 10), 6, (0, 255, 0), -1)
            cv.circle(rgb_img, (x2, height - 10), 6, (0, 255, 0), -1)
            mid_x = int((x1 + x2) / 2.0)
            center_x = mid_x
            cv.line(rgb_img, (mid_x, height - 40), (mid_x, height - 5), (0, 0, 255), 2)
        elif len(contours) == 1:
            # 退化为单线场景：使用单线中心
            M = cv.moments(contours[0])
            cx = int(M['m10'] / max(1.0, M['m00']))
            center_x = cx
            cv.circle(rgb_img, (cx, height - 10), 6, (255, 0, 0), -1)
        else:
            center_x = None

        return rgb_img, binary, center_x

    def execute(self, center_x):
        if self.ros_ctrl.Joy_active is True:
            if self.Start_state is True:
                self.PID_init()
                self.Start_state = False
            return
        self.Start_state = True

        twist = Twist()
        b = Bool()

        # 以图像中心 320 为目标
        error_x = (center_x - 320) * 1.0 / 16
        [z_cmd, _] = self.PID_controller.update([error_x, 0])
        twist.angular.z = -z_cmd if self.img_flip else +z_cmd
        twist.linear.x = self.linear

        if self.warning > 10:
            rospy.loginfo("Obstacles ahead !!!")
            self.ros_ctrl.pub_cmdVel.publish(Twist())
            b.data = True
            self.pub_Buzzer.publish(b)
        else:
            b.data = False
            self.pub_Buzzer.publish(b)
            if abs(center_x - 320) < 40:
                twist.angular.z = 0.0
            self.ros_ctrl.pub_cmdVel.publish(twist)

    def Reset(self):
        self.PID_init()
        self.Track_state = 'init'
        self.hsv_range = ()
        self.ros_ctrl.Joy_active = False
        self.Mouse_XY = (0, 0)
        self.ros_ctrl.pub_cmdVel.publish(Twist())
        rospy.loginfo("Reset success!!!")

    def PID_init(self):
        self.PID_controller = simplePID(
            [0, 0],
            [self.FollowLinePID[0] / 1.0 / (self.scale), 0],
            [self.FollowLinePID[1] / 1.0 / (self.scale), 0],
            [self.FollowLinePID[2] / 1.0 / (self.scale), 0])

    def dynamic_reconfigure_callback(self, config, level):
        self.scale = config['scale']
        self.linear = config['linear']
        self.LaserAngle = config['LaserAngle']
        self.ResponseDist = config['ResponseDist']
        self.FollowLinePID = (config['Kp'], config['Ki'], config['Kd'])
        self.hsv_range = ((config['Hmin'], config['Smin'], config['Vmin']),
                          (config['Hmax'], config['Smax'], config['Vmax']))
        write_HSV(self.hsv_text, self.hsv_range)
        try:
            self.PID_init()
        except Exception:
            pass
        return config

    def registerScan(self, scan_data):
        self.warning = 1
        if not isinstance(scan_data, LaserScan):
            return
        if self.ros_ctrl.Joy_active is True:
            return
        ranges = np.array(scan_data.ranges)
        for i in range(len(ranges)):
            angle = (scan_data.angle_min + scan_data.angle_increment * i) * RAD2DEG
            if abs(angle) > (180 - self.LaserAngle):
                if ranges[i] < self.ResponseDist:
                    self.warning += 1


if __name__ == '__main__':
    node = TwoLineCenterFollower()
    if node.VideoSwitch is False:
        rospy.spin()
    else:
        capture = cv.VideoCapture(0)
        cv_edition = cv.__version__
        if cv_edition[0] == '3':
            capture.set(cv.CAP_PROP_FOURCC, cv.VideoWriter_fourcc(*'XVID'))
        else:
            capture.set(cv.CAP_PROP_FOURCC, cv.VideoWriter.fourcc('M', 'J', 'P', 'G'))
        capture.set(cv.CAP_PROP_FRAME_WIDTH, 640)
        capture.set(cv.CAP_PROP_FRAME_HEIGHT, 480)
        while capture.isOpened():
            start = time.time()
            ret, frame = capture.read()
            action = (cv.waitKey(10) & 0xFF) if node.show_gui else 255
            frame, binary = node.process(frame, action)
            end = time.time()
            fps = 1 / max(1e-6, (end - start))
            text = "FPS : " + str(int(fps))
            cv.putText(frame, text, (30, 30), cv.FONT_HERSHEY_SIMPLEX, 0.6, (100, 200, 200), 1)
            if node.show_gui:
                if isinstance(binary, np.ndarray) and len(binary) != 0:
                    cv.imshow('frame', ManyImgs(1, ([frame, binary])))
                else:
                    cv.imshow('frame', frame)
                if action == ord('q') or action == 113:
                    break
        capture.release()
        if node.show_gui:
            cv.destroyAllWindows()


