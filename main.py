# udp receiver for multicast
import sys, time, socket, struct, threading
from PyQt6 import QtGui
from PyQt6.QtGui import QGuiApplication, QFont, QPainter, QColor, QImage, QMouseEvent
from PyQt6.QtQml import QQmlApplicationEngine, qmlRegisterType, qmlRegisterSingletonType
from PyQt6.QtQuick import QQuickPaintedItem, QQuickItem
from PyQt6.QtCore import Qt,QObject,QRectF,QRect,QSize,pyqtSlot,pyqtSignal
from PyQt6.QtCore import pyqtProperty

import zss_cmd_pb2 as zss
import zss_cmd_type_pb2 as zss_type

MC_ADDR = "225.225.225.225"
MC_PORT = 13134
SEND_PORT = 14234
SINGLE_PORT = 14134

# udp receiver for multicast
def get_ip_address():
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    return ip_address

local_ip=get_ip_address()
print("本机IP地址是:", get_ip_address())
class UdpReceiver:
    def __init__(self, multicast_ip, port,_cb=None):
        self.multicast_ip = multicast_ip
        self.port = port
        self._cb = _cb
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
        self.sock.bind(('', self.port))
        mreq = struct.pack("4sl", socket.inet_aton(self.multicast_ip), socket.INADDR_ANY)
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        self.sock.settimeout(0.2)
    def receive(self,stop_token):
        while True:
            if stop_token():
                break
            try:
                data, addr = self.sock.recvfrom(65535)
                if self._cb is not None:
                    self._cb(data,addr)
            except socket.timeout:
                pass


class PointToPointUdpReceiver:
    def __init__(self, local_ip, local_port,target_ip,_cb):
        self.local_ip = local_ip
        self.local_port = local_port
        self.target_ip = target_ip
        self.receive_flag = False
        self._cb =_cb
        # Create a UDP socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Bind the socket to the local address and port
        self.sock.bind((self.local_ip, self.local_port))
        # Set timeout for socket operations (optional)
        self.sock.settimeout(0.5)
        self.robot_status = zss.Robot_Status()
    def pointreceive(self, stop_token):
        while True:
            if stop_token():
                break
            if self.target_ip is None:
                print("no ip")
                continue
            try:
                print("目标ip:",self.target_ip)
                data, addr = self.sock.recvfrom(65535)
                self.parse_data(data,addr)
                if addr[0] == self.target_ip:  # Check if the message is from the target IP
                    self.robot_status.ParseFromString(data)
                    print("true infrared:",self.robot_status.infrared)
                    if self._cb is not None:
                        self._cb(self.robot_status)
                    #time.sleep(0.01)
                    print("get ip")

            except socket.timeout:
                pass


    def parse_data(self,data,addr):
        self.robot_status = zss.Robot_Status()
        self.robot_status.ParseFromString(data)
        print(self.robot_status.robot_id)
        print(self.robot_status.infrared)


class UdpSender:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    def send(self, msg, addr):
        self.sock.sendto(msg, addr)

class InfoReceiver:
    info = {}
    selected = {}
    def __init__(self,info_cb = None):
        self.info = {}
        self.info_cb = info_cb
    def _cb(self,data,addr):
        pb_info = zss.Multicast_Status()
        pb_info.ParseFromString(data)
        pb_info.ip = addr[0]
        self.info[addr[0]] = pb_info
        if self.info_cb is not None:
            self.info_cb(pb_info.robot_id,pb_info)
class CmdSender:
    def __init__(self):
        self.udpSender = UdpSender()
        self.pb_data = zss.Robot_Command()
        pass
    # updateCommandParams(int robotID,double velX,double velY,double velR,double ctrl,bool mode,bool shoot,double power)
    def updateCommandParams(self,robotID,velX,velY,velR,ctrl,mode,shoot,power):
        self.pb_data = zss.Robot_Command()
        self.pb_data.robot_id = -1
        self.pb_data.kick_mode = zss.Robot_Command.KickMode.NONE if not shoot else (zss.Robot_Command.KickMode.CHIP if mode else zss.Robot_Command.KickMode.KICK)
        # self.pb_data.desire_power = power
        self.pb_data.kick_discharge_time = power
        self.pb_data.dribble_spin = ctrl
        self.pb_data.cmd_type = zss.Robot_Command.CmdType.CMD_VEL
        self.pb_data.cmd_vel.velocity_x = velX
        self.pb_data.cmd_vel.velocity_y = velY
        self.pb_data.cmd_vel.velocity_r = velR
        self.pb_data.comm_type = zss.Robot_Command.CommType.UDP_WIFI
        print("updateCommandParams",str(self.pb_data))

    def sendCommand(self,infoReceiver:InfoReceiver):
        # print("sendCommand",str(self.pb_data))
        for id,info in infoReceiver.selected.items():
            self.pb_data.robot_id = id
            # Serialize
            data = self.pb_data.SerializeToString()
            self.udpSender.send(data,(info.ip,SEND_PORT))

#inforeceiver的拿到了一个paintinfo的回调函数 udprecv开了一个线程 一直执行receive 收到了就执行inforeceriver的本身的回调函数填数组 再执行paintinfo
class InfoViewer(QQuickPaintedItem):
    MAX_PLAYER = 16
    drawSignal = pyqtSignal(int,zss.Multicast_Status)
    statusSingnal=pyqtSignal(zss.Robot_Status)
    flag1=0
    flag2=0
    update_control=0
    def __init__(self,parent=None):
        super().__init__(parent)
        # accept mouse event left click
        self.setAcceptedMouseButtons(Qt.MouseButton.LeftButton | Qt.MouseButton.RightButton)
        self.receiverNeedStop = False
        self.infoReceiver = InfoReceiver(self.getNewInfo)
        self.cmdSender = CmdSender()
        udpRecv = UdpReceiver(MC_ADDR,MC_PORT,self.infoReceiver._cb) #PAIN
        #self.pointtopointRecv =PointToPointUdpReceiver(local_ip,SINGLE_PORT,None)
        self.pointtopointRecv = PointToPointUdpReceiver(local_ip, SINGLE_PORT, None,self.paint_signal)
        t = threading.Thread(target=udpRecv.receive,args=(lambda : self.receiverNeedStop,))
        t.start()
        t1 = threading.Thread(target=self.pointtopointRecv.pointreceive,args=(lambda : self.receiverNeedStop,))
        t1.start()
        self.painter = QPainter()

        self.image = QImage(QSize(int(self.width()),int(self.height())),QImage.Format.Format_ARGB32_Premultiplied)
        self.ready = False
        self.drawSignal.connect(self.paintInfo)
        self.statusSingnal.connect(self.paint_single_info)
    @pyqtSlot()
    def close(self):
        print("closing info viewer, stop recv thread")
        self.receiverNeedStop = True

    def getNewInfo(self,n,info):
        # print("got new info ",n,info)
        if self.ready and self.painter.isActive() and n >= 0 and n < self.MAX_PLAYER:
            self.drawSignal.emit(n,info)
    def mousePressEvent(self, event: QMouseEvent) -> None:
        index = self.getAreaIndex(event.pos())
        for info in self.infoReceiver.info.values():
            if info.robot_id == index:
                if event.button() == Qt.MouseButton.LeftButton:
                    self.infoReceiver.selected.clear()
                else :
                    if index in self.infoReceiver.selected:
                        self.infoReceiver.selected.pop(index)
                        self.pointtopointRecv.receive_flag = False
                        self.drawSignal.emit(index,info)
                        return
                self.infoReceiver.selected[index] = info
                self.pointtopointRecv.target_ip= info.ip
                self.pointtopointRecv.receive_flag = True
                self.drawSignal.emit(index,info)
                break
    @pyqtSlot(int,zss.Multicast_Status)
    def paintInfo(self,n,info):
        # fill background
        self.painter.setPen(QColor(255,255,255))
        self.painter.setBrush(QColor(255,255,255))
        self.painter.drawRect(QRectF(self._x(n,0.0), self._y(n,0.0), self._w(n,0.3),self._h(n,1.0)))
        #self.painter.drawRect(QRectF(self._x(10, 0.35), self._y(10, 0.0), self._w(10, 1.0), self._h(10, 1.0)))

        self.painter.setPen(QColor(0,0,0) if n not in self.infoReceiver.selected else QColor(255,0,0))
        self.painter.setBrush(Qt.BrushStyle.NoBrush)
        self.painter.setFont(QFont('Arial', 10))
        #print("infraraed:",self.pointtopointRecv.robot_status.infrared)
        self.painter.drawRect(QRectF(self._x(n,0.01), self._y(n,0.05), self._w(n,0.28),self._h(n,0.9)))
        self.painter.drawText(QRectF(self._x(n,0.0), self._y(n,0.0), self._w(n,0.3),self._h(n,1.0)), Qt.AlignmentFlag.AlignCenter, info.ip)
        #if self.pointtopointRecv.receive_flag is True:
         #   self.painter.drawText(QRectF(self._x(10,0.35), self._y(10,0.0), self._w(10,1.0), self._h(10,1.0)),Qt.AlignmentFlag.AlignCenter, self.pointtopointRecv.robot_status.infrared)




        self.update(self._area(n))
    def paint(self, painter):
        if self.ready:
            painter.drawImage(QRectF(0,0,self.width(),self.height()),self.image)
        pass
    @pyqtSlot(int,int)
    def resize(self,width,height):
        self.ready = False
        if width <=0 or height <=0:
            return
        if self.painter.isActive():
            self.painter.end()
        self.image = QImage(QSize(width,height),QImage.Format.Format_ARGB32_Premultiplied)
        self.painter.begin(self.image)
        self.ready = True
    def getAreaIndex(self,pos):
        yIndex = int(pos.y()/(self.height()/self.MAX_PLAYER))
        return yIndex
    def _area(self,n):
        return QRect(int(self._x(n,0)), int(self._y(n,0)), int(self._w(n,1)),int(self._h(n,1)))
    def _x(self,n,v):
        return self.width()*(v)
    def _y(self,n,v):
        return self.height()/self.MAX_PLAYER*(n+v)
    def _w(self,n,v):
        return self.width()*(v)
    def _h(self,n,v):
        return self.height()/self.MAX_PLAYER*(v)
    @pyqtSlot(int,float,float,float,float,bool,bool,float)
    def updateCommandParams(self,robotID,velX,velY,velR,ctrl,mode,shoot,power):
        self.cmdSender.updateCommandParams(robotID,velX,velY,velR,ctrl,mode,shoot,power)
    @pyqtSlot()
    def sendCommand(self):
        self.cmdSender.sendCommand(self.infoReceiver)

    def paint_signal(self,info):
        if self.ready and self.painter.isActive():
            #self.flag1=self.flag1+1
            #print("flag1:",self.flag1)
            self.statusSingnal.emit(info)

    @pyqtSlot(zss.Robot_Status)
    def paint_single_info(self,info):
        #print("what")
        #self.flag2 = self.flag2 + 1
        #print("flag2:", self.flag2)
        #self.painter=QPainter()
        #self.painter.begin(self)

        self.painter.setPen(QColor(255,255,255))
        self.painter.setBrush(QColor(173, 216, 230))
        for i in range(16):
            self.painter.drawRect(QRectF(self._x(i,0.32), self._y(i,0.0), self._w(i,1.0),self._h(i,1.0)))
        #self.painter.drawRect(QRectF(self._x(10, 0.35), self._y(10, 0.0), self._w(10, 1.0), self._h(10, 1.0)))
        self.painter.setFont(QFont('Helvetica', 12))
        self.painter.setPen(QColor(0,0,0))

        if self.pointtopointRecv.receive_flag is True:

            battery_str = "{:.3f}".format(info.battery)
            capacitance_str = "{:.3f}".format(info.capacitance)
            if info.team ==1:
                team="蓝"
            else :
                team="黄"
            angle_z_str="{:.3f}".format(info.imu_data[10])
            angle_y_str = "{:.3f}".format(info.imu_data[9])
            angle_x_str = "{:.3f}".format(info.imu_data[8])
            w_x_str="{:.3f}".format(info.imu_data[4])
            w_y_str = "{:.3f}".format(info.imu_data[5])
            w_z_str = "{:.3f}".format(info.imu_data[6])
            wheel0_str="{:.3f}".format(info.wheel_encoder[0])
            wheel1_str = "{:.3f}".format(info.wheel_encoder[1])
            wheel2_str = "{:.3f}".format(info.wheel_encoder[2])
            wheel3_str = "{:.3f}".format(info.wheel_encoder[3])
            self.painter.drawText(QRectF(self._x(0, 0.35), self._y(0, 0.0), self._w(0, 1.0), self._h(0, 1.0)),
                                  Qt.AlignmentFlag.AlignLeft| Qt.AlignmentFlag.AlignVCenter, "车号： " + str(info.robot_id)+"                                  ")
            self.painter.drawText(QRectF(self._x(1, 0.35), self._y(1, 0.0), self._w(1, 1.0), self._h(1, 1.0)),
                                  Qt.AlignmentFlag.AlignLeft| Qt.AlignmentFlag.AlignVCenter, "车队：  " + str(team)+"                                  ")
            self.painter.drawText(QRectF(self._x(2, 0.35), self._y(2, 0.0), self._w(2, 1.0), self._h(2, 1.0)),
                                  Qt.AlignmentFlag.AlignLeft| Qt.AlignmentFlag.AlignVCenter, "0 号轮速度：  " + str(wheel0_str)+"                                  ")
            self.painter.drawText(QRectF(self._x(3, 0.35), self._y(3, 0.0), self._w(3, 1.0), self._h(3, 1.0)),
                                  Qt.AlignmentFlag.AlignLeft| Qt.AlignmentFlag.AlignVCenter, "1 号轮速度：   " + str(wheel1_str)+"                                  ")
            self.painter.drawText(QRectF(self._x(4, 0.35), self._y(4, 0.0), self._w(4, 1.0), self._h(4, 1.0)),
                                  Qt.AlignmentFlag.AlignLeft| Qt.AlignmentFlag.AlignVCenter, "2 号轮速度：   " + str(wheel2_str)+"                                  ")
            self.painter.drawText(QRectF(self._x(5, 0.35), self._y(5, 0.0), self._w(5, 1.0), self._h(5, 1.0)),Qt.AlignmentFlag.AlignLeft| Qt.AlignmentFlag.AlignVCenter, "3 号轮速度：   " + str(wheel3_str)+"                                  ")
            self.painter.drawText(QRectF(self._x(6, 0.35), self._y(6, 0.0), self._w(6, 1.0), self._h(6, 1.0)),Qt.AlignmentFlag.AlignLeft| Qt.AlignmentFlag.AlignVCenter, "电容电压/V " + capacitance_str+"                                  ")
            self.painter.drawText(QRectF(self._x(7, 0.35), self._y(7, 0.0), self._w(7, 1.0), self._h(7, 1.0)),Qt.AlignmentFlag.AlignLeft| Qt.AlignmentFlag.AlignVCenter, "电池电量/V " + battery_str+"                                  ")
            self.painter.drawText(QRectF(self._x(8,0.35), self._y(8,0.0), self._w(8,1.0), self._h(8,1.0)),Qt.AlignmentFlag.AlignLeft| Qt.AlignmentFlag.AlignVCenter, "红外时间 "+str(info.infrared)+"                                  ")
            self.painter.drawText(QRectF(self._x(9, 0.35), self._y(9, 0.0), self._w(9, 1.0), self._h(9, 1.0)),
                                  Qt.AlignmentFlag.AlignLeft| Qt.AlignmentFlag.AlignVCenter, "x 轴角度 " + str(angle_x_str)+"                                  ")
            self.painter.drawText(QRectF(self._x(10, 0.35), self._y(10, 0.0), self._w(10, 1.0), self._h(10, 1.0)),
                                  Qt.AlignmentFlag.AlignLeft| Qt.AlignmentFlag.AlignVCenter, "y 轴角度 " + str(angle_y_str)+"                                  ")
            self.painter.drawText(QRectF(self._x(11, 0.35), self._y(11, 0.0), self._w(11, 1.0), self._h(11, 1.0)),
                                  Qt.AlignmentFlag.AlignLeft| Qt.AlignmentFlag.AlignVCenter, "z 轴角度 " + str(angle_z_str)+"                                  ")

            self.painter.drawText(QRectF(self._x(12, 0.35), self._y(12, 0.0), self._w(12, 1.0), self._h(12, 1.0)),
                                  Qt.AlignmentFlag.AlignLeft| Qt.AlignmentFlag.AlignVCenter, "x 轴角加角度 " + w_x_str+"                                  ")
            self.painter.drawText(QRectF(self._x(13, 0.35), self._y(13, 0.0), self._w(13, 1.0), self._h(13, 1.0)),
                                  Qt.AlignmentFlag.AlignLeft| Qt.AlignmentFlag.AlignVCenter, "y 轴角加角度 " + w_y_str+"                                  ")
            self.painter.drawText(QRectF(self._x(14, 0.35), self._y(14, 0.0), self._w(14, 1.0), self._h(14, 1.0)),
                                  Qt.AlignmentFlag.AlignLeft| Qt.AlignmentFlag.AlignVCenter, "z 轴角加角度 " + w_z_str+"                                  ")
            self.painter.drawText(QRectF(self._x(15, 0.35), self._y(15, 0.0), self._w(15, 1.0), self._h(15, 1.0)),
                                  Qt.AlignmentFlag.AlignLeft| Qt.AlignmentFlag.AlignVCenter,
                                  "广告位招租 zjunlict" + "                                  ")


        self.update()

if __name__ == '__main__':
    app = QGuiApplication(sys.argv)
    engine = QQmlApplicationEngine()
    qmlRegisterType(InfoViewer, 'ZSS', 1, 0, 'InfoViewer')
    # 创建 InfoViewer 实例
    # 连接退出信号
    engine.quit.connect(app.quit)
    # 加载QML文件
    try:
        engine.load('main.qml')
    except Exception as e:
        print("Failed to load QML:", e)
        sys.exit(1)
    # 执行应用程序
    res = app.exec()
    # 清理资源
    del engine
    sys.exit(res)
    # udpSender = UdpSender()
    # while True:
    #     time.sleep(1)
