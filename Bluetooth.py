from bluetooth import *
import dbus # Used to set up the SDP record
class Bluetooth:
    """docstring for Gamepad"""
    HOST = "B8:27:EB:A7:A4:55"
    PORT = 1
    P_CTRL = 17
    P_INTR = 19
    UUID = "1f16e7c0-b59b-11e3-95d2-0002a5d5c51b"
    def __init__(self, sdp, classname, devname):
        self.classname = classname
        self.devname = devname
        self.soccontrol = BluetoothSocket(L2CAP)
        self.sockinter = BluetoothSocket(L2CAP)

        self.soccontrol.bind(("", Bluetooth.P_CTRL))
        self.sockinter.bind(("",Bluetooth.P_INTR))

        self.bus = dbus.SystemBus()

        try:
            self.objManager = dbus.Interface(self.bus.get_object("org.bluez", "/"),
                                          "org.freedesktop.DBus.ObjectManager")
            #print self.manager.GetManagedObjects()["/org/bluez/hci0"]
            self.manager = dbus.Interface(self.bus.get_object("org.bluez", "/org/bluez"),
                                          "org.bluez.ProfileManager1")
            self.hci_props = dbus.Interface(self.bus.get_object("org.bluez", "/org/bluez/hci0"),
                                                                    "org.freedesktop.DBus.Properties")
        except:
            print sys.exc_info()
            sys.exit("[FATAL] Could not set up Bluez5")

        try:
            fh = open(sdp,"r")
        except Exception, e:
            sys.exit("Cannot open sdp_record file, " + str(e))
        self.service_record = fh.read()
        fh.close()
        try:
            opts = {
                "AutoConnect": True,
                "ServiceRecord":self.service_record,
                "Role":"server",
                "RequireAuthentication":True,
                "RequireAuthorization":True
            }
            self.manager.RegisterProfile("/org/bluez/hci0", self.UUID, opts)
            
            print "Service Record saved!"
        except:
            print "Service Records saved. Probably already exists"

    def listen(self):
        os.system("sudo hciconfig hci0 class "+self.classname)
        os.system("sudo hciconfig hci0 name "+self.devname)
        os.system("hciconfig hci0 piscan")
		
        self.soccontrol.listen(1)
        self.sockinter.listen(1)
        print "waiting for connection"
        self.ccontrol, self.cinfo = self.soccontrol.accept()
        print "Control channel connected to "+self.cinfo[Bluetooth.HOST]
        self.cinter, self.cinfo = self.sockinter.accept()
        print "Interrupt channel connected to "+self.cinfo[Bluetooth.HOST] 

    def sendInput(self, inp):
        str_inp = ""
        for elem in inp:
            if type(elem) is list:
                tmp_str = ""
                for tmp_elem in elem:
                    tmp_str += str(tmp_elem)
                for i in range(0,len(tmp_str)/8):
                    if((i+1)*8 >= len(tmp_str)):
                        str_inp += chr(int(tmp_str[i*8:],2))
                    else:
                        str_inp += chr(int(tmp_str[i*8:(i+1)*8],2))
            else:
                str_inp += chr(elem)
        self.cinter.send(str_inp)