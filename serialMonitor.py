import serial
import threading

class SerialMonitor(threading.Thread):

    def __init__(self, comPort, baudRate = 9600):
        self.comPort = comPort
        self.baudRate = baudRate
        self.serialConnection = serial.Serial(comPort, baudRate)
        self.lineReady = False
        self.currentLine = None
        self.lock = threading.Lock()
        super(SerialMonitor, self).__init__()


    def run(self):
        while True:
            line = self.getLineFromComPort()
            self.lock.acquire()
            self.currentLine = line
            self.lineReady = True
            self.lock.release()
        
    def displaySerialMonitor(self):
        if self.dataIsAvailable:
            serialMonitorData = self.getLineFromComPort()
            print(serialMonitorData, end= '')
        
    def getIntFromComPort(self):
        serialData = self.getLineFromComPort()
        return int(serialData)

    def getFloatFromComPort(self):
        serialData = self.getLineFromComPort()
        return float(serialData)

    def getLineFromComPort(self):
        line = ''
        lastCharReceived = ''
        while '\n' not in lastCharReceived: #a new line signals the end of a line
            lastCharReceived = self.getCharFromComPort()
            line += lastCharReceived

        return line

    def getCurrentLine(self):
        self.lock.acquire()
        self.lineReady = False
        lineToReturn  = self.currentLine + ""
        self.lock.release()
        return lineToReturn

    def getCharFromComPort(self):
        try:
            return self.getByteFromComPort().decode('utf-8')
        except:
            return ""
        
    def getByteFromComPort(self):
        return self.serialConnection.read()

    def dataIsAvailable():
        if self.serialConnection.in_waiting > 0:
            return True

    def sendNumToComPort(self, numToSend):
        numAsString = str(numToSend)
        self.sendStringToComPort(numAsString)

    def sendStringToComPort(self, message):
        self.sendBytesToComPort(message.encode('utf-8'))

    def sendBytesToComPort(self, bytesToSend):
        self.serialConnection.write(bytesToSend)


if __name__ == "__main__":
    comPort = "COM28"
    newMonitor = SerialMonitor(comPort)
    newMonitor.start()
    while True:
        if newMonitor.lineReady:
            print(newMonitor.getCurrentLine())

        command = input(">>:")
        if len(command):
            newMonitor.sendStringToComPort(command + "\n")
