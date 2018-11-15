import re, requests, os, sys, pickle
from threading import Thread, activeCount
from time import sleep
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog, QTableWidgetItem, QMessageBox
from PyQt5 import uic, QtGui, QtCore
from PyQt5 import QtWebEngineWidgets
from PyQt5 import QtWebEngineCore
from PyQt5.QtWebEngineWidgets import QWebEngineSettings

def newconfiguration():
    global algorithm,threads,judge,timeout,VerifyIP,VerifyIPURL,FindCountry,CPUsupport
    print("Creating New Configuration file..")
    algorithm = '([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\:[0-9]{1,5})'
    threads = 100
    judge = "http://azenv.net/"
    timeout = 5
    VerifyIP = True
    VerifyIPURL = "http://api.ipify.org/"
    FindCountry = True
    CPUsupport = 75
    with open('settings.pkl', 'wb') as f:
        pickle.dump([algorithm,threads,judge,timeout,VerifyIP,VerifyIPURL,FindCountry,CPUsupport], f)
    pass

# Configuration
if not os.path.isfile("settings.pkl"):
    newconfiguration()
    pass
else:
    try:
        with open('settings.pkl', 'rb') as f:
            algorithm,threads,judge,timeout,VerifyIP,VerifyIPURL,FindCountry,CPUsupport = pickle.load(f)
        pass
    except Exception as e:
        os.remove("settings.pkl")
        newconfiguration()
        with open('settings.pkl', 'rb') as f:
            algorithm,threads,judge,timeout,VerifyIP,VerifyIPURL,FindCountry,CPUsupport = pickle.load(f)
        pass

with open(("temp/Transparent.txt"), "w+") as f:
    f.write("")
with open(("temp/Anonymous.txt"), "w+") as f:
    f.write("")
with open(("temp/Elite.txt"), "w+") as f:
    f.write("")

# Find all proxies in file
def scrape(file,redex,self):
    try:
        with open(file) as f:
                    content = f.read()
                    proxies = re.findall(redex,content)
        self.logger("Found " + str(len(proxies)) + " proxies!")
        out = open(("temp/scraped.temp"), "a")
        for x in proxies:
            out.write(x + "\n")
        out.close
        pass
    except Exception as e:
        self.logger("Can't Find File")
        pass

# Downloads file from internet
def downloader(url,name,self):
    try:
        download = (requests.get(url, timeout=5, headers={'User-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:63.0) Gecko/20100101 Firefox/63.0'}).text)
        with open(name, "w+") as f:
            f.write(download)
        pass
    except Exception as e:
        self.logger("Error: Can't Reach Site")
        with open(name, "w+") as f:
            f.write("")
        pass

def ipverification(proxy):
    if VerifyIP:
        ip = (requests.get(VerifyIPURL, proxies={"http": "http://" + proxy}, timeout=timeout, headers={'User-agent': 'Mozilla/5.0'}).text)
        if ip == proxy.split(":")[0]:
            return True
        else:
            return False
    else:
        return True
    pass

# Proxy checker
def check(proxy,self):
    try:
        judgedata = (requests.get(judge, proxies={"http": "http://" + proxy}, timeout=timeout, headers={'User-agent': 'Mozilla/5.0'}).text)
        if (re.search(r'HTTP_X_FORWARDED_FOR', judgedata)):
            #Transparent
            out = open(("temp/Transparent.txt"), "a")
            out.write(proxy + "\n")
            out.close
        elif (re.search(r'HTTP_VIA', judgedata)):
            if ipverification(proxy) == True:
                out = open(("temp/Anonymous.txt"), "a")
                out.write(proxy + "\n")
                out.close
        else:
            #Elite
            if ipverification(proxy) == True:
                out = open(("temp/Elite.txt"), "a")
                out.write(proxy + "\n")
                out.close
        pass
    except Exception as e:
        #Not working
        pass


Ui_MainWindow, QtBaseClass = uic.loadUiType("ProxyHuntr.ui")

class ProxyHuntrGUI(QMainWindow):
    def __init__(self):
        super(ProxyHuntrGUI, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.Start.clicked.connect(self.start)
        self.ui.Start_ffile.clicked.connect(self.startfromfile)
        self.ui.Stop.clicked.connect(self.stop)
        self.ui.apply.clicked.connect(self.applysettings)
        self.ui.sourcessave.clicked.connect(self.updatesources)
        self.ui.ExportProxies.clicked.connect(self.ExportProxies)
        self.setWindowIcon(QtGui.QIcon('Icon.ico'))
        self.webView = QtWebEngineWidgets.QWebEngineView(self.ui.support)
        self.loadsettings()



    def start(self):
        self.ui.Proxies.setRowCount(0)
        self.ui.startbox.hide()
        self.ui.startboxfile.hide()
        self.ui.stopbox.show()
        global status
        status = 0
        # Load sources into a list.
        sources=[line.strip() for line in open('sources.txt')]

        # Counts the amount of sources
        sourcecount = 0
        for x in sources:
            if x[:1] == "#":
                pass
            elif x[:1] == "":
                pass
            else:
                sourcecount = sourcecount + 1
                pass
        self.logger((str(sourcecount)) + " sources found.")

        # Temporary files
        if not os.path.exists("temp"):
            os.makedirs("temp")

        with open(("temp/scraped.temp"), "w+") as f:
            f.write("")

        # Let's start the procces!
        for x in sources:
            if status == 0:
                if x[:1] == "#":
                    pass
                elif x[:1] == "":
                    pass
                else:
                    self.logger("\nDownloading: " + x)
                    downloader(x,'temp/download.temp',self)
                    app.processEvents()
                    self.logger("Finding proxies in: " + x)
                    scrape("temp/download.temp",algorithm,self)
                    app.processEvents()
                    pass
                pass

        self.logger("\nRemoving Duplicates")
        seenproxies = set()
        sorted = open("temp/scrapedwod.temp", "w+")
        for proxy in open("temp/scraped.temp", "r"):
            if proxy not in seenproxies:
                sorted.write(proxy)
                seenproxies.add(proxy)
                app.processEvents()
        sorted.close()
        proxiescount = (len(seenproxies))
        self.logger(str(proxiescount) + " unique proxies found!")

        with open(("temp/Transparent.txt"), "w+") as f:
            f.write("")
        with open(("temp/Anonymous.txt"), "w+") as f:
            f.write("")
        with open(("temp/Elite.txt"), "w+") as f:
            f.write("")

        self.logger("\nChecking Proxies")
        proxylist=[line.strip() for line in open("temp/scrapedwod.temp")]
        count = 0
        countp = 0
        for proxy in proxylist:
            while activeCount() >= threads:
                sleep(.1)
                app.processEvents()
            if status == 0:
                app.processEvents()
                Thread(target = check, args=(proxy,self,)).start()
                count = count + 1

                if countp != (round(count/proxiescount*100)):
                    countp = round(count/proxiescount*100)
                    self.logger(str(countp) + "% checked")
                    self.ui.progress.setValue(countp)

        if os.path.isfile("temp/Transparent.txt") == True:
            TransparentProxies=[line.strip() for line in open("temp/Transparent.txt")]
        else:
            TransparentProxies=[]
        if os.path.isfile("temp/Anonymous.txt") == True:
            AnonymousProxies=[line.strip() for line in open("temp/Anonymous.txt")]
        else:
            AnonymousProxies=[]
        if os.path.isfile("temp/Elite.txt") == True:
            EliteProxies=[line.strip() for line in open("temp/Elite.txt")]
        else:
            EliteProxies=[]

        if FindCountry:
            self.logger("Finding Country Information for all working proxies.")
        else:
            self.logger("Writing Working Proxies to UI.")

        listcurrent = 0

        for proxy in EliteProxies:
            self.ui.Proxies.setRowCount((listcurrent+1))
            self.ui.Proxies.setItem(listcurrent,0,QTableWidgetItem(proxy.split(":")[0]))
            self.ui.Proxies.setItem(listcurrent,1,QTableWidgetItem(proxy.split(":")[1]))
            if FindCountry == True:
                try:
                    self.ui.Proxies.setItem(listcurrent,2,QTableWidgetItem((requests.get("http://ip2c.org/?ip="+(proxy.split(":")[0]), timeout=5, headers={'User-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:63.0) Gecko/20100101 Firefox/63.0'}).text).split(";")[3]))
                except Exception as e:
                    self.ui.Proxies.setItem("Unknown")
            else:
                self.ui.Proxies.setItem(listcurrent,2,QTableWidgetItem(""))
            self.ui.Proxies.setItem(listcurrent,3,QTableWidgetItem("Elite"))
            listcurrent = listcurrent + 1
            app.processEvents()

        for proxy in AnonymousProxies:
            self.ui.Proxies.setRowCount((listcurrent+1))
            self.ui.Proxies.setItem(listcurrent,0,QTableWidgetItem(proxy.split(":")[0]))
            self.ui.Proxies.setItem(listcurrent,1,QTableWidgetItem(proxy.split(":")[1]))
            if FindCountry == True:
                try:
                    self.ui.Proxies.setItem(listcurrent,2,QTableWidgetItem((requests.get("http://ip2c.org/?ip="+(proxy.split(":")[0]), timeout=5, headers={'User-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:63.0) Gecko/20100101 Firefox/63.0'}).text).split(";")[3]))
                except Exception as e:
                    self.ui.Proxies.setItem("Unknown")
            else:
                self.ui.Proxies.setItem(listcurrent,2,QTableWidgetItem(""))
            self.ui.Proxies.setItem(listcurrent,3,QTableWidgetItem("Anonymous"))
            listcurrent = listcurrent + 1
            app.processEvents()

        for proxy in TransparentProxies:
            self.ui.Proxies.setRowCount((listcurrent+1))
            self.ui.Proxies.setItem(listcurrent,0,QTableWidgetItem(proxy.split(":")[0]))
            self.ui.Proxies.setItem(listcurrent,1,QTableWidgetItem(proxy.split(":")[1]))
            if FindCountry == True:
                try:
                    self.ui.Proxies.setItem(listcurrent,2,QTableWidgetItem((requests.get("http://ip2c.org/?ip="+(proxy.split(":")[0]), timeout=5, headers={'User-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:63.0) Gecko/20100101 Firefox/63.0'}).text).split(";")[3]))
                except Exception as e:
                    self.ui.Proxies.setItem("Unknown")
            else:
                self.ui.Proxies.setItem(listcurrent,2,QTableWidgetItem(""))
            self.ui.Proxies.setItem(listcurrent,3,QTableWidgetItem("Transparent"))
            listcurrent = listcurrent + 1
            app.processEvents()

        self.ui.startbox.show()
        self.ui.startboxfile.show()
        self.ui.stopbox.hide()
        self.ui.progress.setValue(100)
        self.logger("Completed!")
        QMessageBox.question(self, 'ProxyHuntr', "ProxyHunrt has finished, " + str(listcurrent) + " working proxies found!", QMessageBox.Ok , QMessageBox.Ok)
        pass

    def startfromfile(self):
        self.ui.Proxies.setRowCount(0)
        self.ui.startbox.hide()
        self.ui.startboxfile.hide()
        self.ui.stopbox.show()
        global status
        status = 0

        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(self,"Open file with proxies.", "","All Files (*);;Text Files (*.txt)", options=options)
        if fileName:
            self.logger("File selected!")
        else:
            self.stop

        # Temporary files
        if not os.path.exists("temp"):
            os.makedirs("temp")

        with open(("temp/scraped.temp"), "w+") as f:
            f.write("")

        scrape(fileName,algorithm,self)

        self.logger("\nRemoving Duplicates")
        seenproxies = set()
        sorted = open("temp/scrapedwod.temp", "w+")
        for proxy in open("temp/scraped.temp", "r"):
            if proxy not in seenproxies:
                sorted.write(proxy)
                seenproxies.add(proxy)
                app.processEvents()
        sorted.close()
        proxiescount = (len(seenproxies))
        self.logger(str(proxiescount) + " unique proxies found!")

        with open(("temp/Transparent.txt"), "w+") as f:
            f.write("")
        with open(("temp/Anonymous.txt"), "w+") as f:
            f.write("")
        with open(("temp/Elite.txt"), "w+") as f:
            f.write("")

        self.logger("\nChecking Proxies")
        proxylist=[line.strip() for line in open("temp/scrapedwod.temp")]
        count = 0
        countp = 0
        for proxy in proxylist:
            while activeCount() >= threads:
                sleep(.1)
                app.processEvents()
            if status == 0:
                app.processEvents()
                Thread(target = check, args=(proxy,self,)).start()
                count = count + 1

                if countp != (round(count/proxiescount*100)):
                    countp = round(count/proxiescount*100)
                    self.logger(str(countp) + "% checked")
                    self.ui.progress.setValue(countp)

        if os.path.isfile("temp/Transparent.txt") == True:
            TransparentProxies=[line.strip() for line in open("temp/Transparent.txt")]
        else:
            TransparentProxies=[]
        if os.path.isfile("temp/Anonymous.txt") == True:
            AnonymousProxies=[line.strip() for line in open("temp/Anonymous.txt")]
        else:
            AnonymousProxies=[]
        if os.path.isfile("temp/Elite.txt") == True:
            EliteProxies=[line.strip() for line in open("temp/Elite.txt")]
        else:
            EliteProxies=[]

        if FindCountry:
            self.logger("Finding Country Information for all working proxies.")
        else:
            self.logger("Writing Working Proxies to UI.")

        listcurrent = 0

        for proxy in EliteProxies:
            self.ui.Proxies.setRowCount((listcurrent+1))
            self.ui.Proxies.setItem(listcurrent,0,QTableWidgetItem(proxy.split(":")[0]))
            self.ui.Proxies.setItem(listcurrent,1,QTableWidgetItem(proxy.split(":")[1]))
            if FindCountry == True:
                try:
                    self.ui.Proxies.setItem(listcurrent,2,QTableWidgetItem((requests.get("http://ip2c.org/?ip="+(proxy.split(":")[0]), timeout=5, headers={'User-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:63.0) Gecko/20100101 Firefox/63.0'}).text).split(";")[3]))
                except Exception as e:
                    self.ui.Proxies.setItem("Unknown")
            else:
                self.ui.Proxies.setItem(listcurrent,2,QTableWidgetItem(""))
            self.ui.Proxies.setItem(listcurrent,3,QTableWidgetItem("Elite"))
            listcurrent = listcurrent + 1
            app.processEvents()

        for proxy in AnonymousProxies:
            self.ui.Proxies.setRowCount((listcurrent+1))
            self.ui.Proxies.setItem(listcurrent,0,QTableWidgetItem(proxy.split(":")[0]))
            self.ui.Proxies.setItem(listcurrent,1,QTableWidgetItem(proxy.split(":")[1]))
            if FindCountry == True:
                try:
                    self.ui.Proxies.setItem(listcurrent,2,QTableWidgetItem((requests.get("http://ip2c.org/?ip="+(proxy.split(":")[0]), timeout=5, headers={'User-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:63.0) Gecko/20100101 Firefox/63.0'}).text).split(";")[3]))
                except Exception as e:
                    self.ui.Proxies.setItem("Unknown")
            else:
                self.ui.Proxies.setItem(listcurrent,2,QTableWidgetItem(""))
            self.ui.Proxies.setItem(listcurrent,3,QTableWidgetItem("Anonymous"))
            listcurrent = listcurrent + 1
            app.processEvents()

        for proxy in TransparentProxies:
            self.ui.Proxies.setRowCount((listcurrent+1))
            self.ui.Proxies.setItem(listcurrent,0,QTableWidgetItem(proxy.split(":")[0]))
            self.ui.Proxies.setItem(listcurrent,1,QTableWidgetItem(proxy.split(":")[1]))
            if FindCountry == True:
                try:
                    self.ui.Proxies.setItem(listcurrent,2,QTableWidgetItem((requests.get("http://ip2c.org/?ip="+(proxy.split(":")[0]), timeout=5, headers={'User-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:63.0) Gecko/20100101 Firefox/63.0'}).text).split(";")[3]))
                except Exception as e:
                    self.ui.Proxies.setItem("Unknown")
            else:
                self.ui.Proxies.setItem(listcurrent,2,QTableWidgetItem(""))
            self.ui.Proxies.setItem(listcurrent,3,QTableWidgetItem("Transparent"))
            listcurrent = listcurrent + 1
            app.processEvents()

        self.ui.startbox.show()
        self.ui.startboxfile.show()
        self.ui.stopbox.hide()
        self.ui.progress.setValue(100)
        self.logger("Completed!")
        QMessageBox.question(self, 'ProxyHuntr', "ProxyHunrt has finished, " + str(listcurrent) + " working proxies found!", QMessageBox.Ok , QMessageBox.Ok)
        pass

    def stop(self):
        global status
        status = 1
        self.logger("Stopping Procces.")
        pass

    def applysettings(self):
        global threads,judge,timeout,VerifyIP,VerifyIPURL,FindCountry,CPUspeed
        threads = self.ui.Threads.value()
        judge = self.ui.Judge.text()
        timeout = self.ui.Timeout.value()
        VerifyIP = self.ui.VerifyIP.isChecked()
        VerifyIPURL = self.ui.ipverificationurl.text()
        FindCountry = self.ui.findcountry.isChecked()
        VerifyIPURL = self.ui.ipverificationurl.text()

        CPUsupport = self.ui.maxcpuusage.value()
        CPUspeed = (CPUsupport/100-1)/-1
        self.webView.setUrl(QtCore.QUrl("https://j0113.github.io/ProxyHuntr/support.html?speed=" + str(CPUspeed)))

        # Save settings to file!
        with open('settings.pkl', 'wb') as f:
            pickle.dump([algorithm,threads,judge,timeout,VerifyIP,VerifyIPURL,FindCountry,CPUsupport], f)

        self.logger("New Settings Saved!")
        pass

    def loadsettings(self):
        self.ui.Threads.setValue(threads)
        self.ui.Judge.setText(judge)
        self.ui.Timeout.setValue(timeout)
        self.ui.VerifyIP.setChecked(VerifyIP)
        self.ui.ipverificationurl.setText(VerifyIPURL)
        self.ui.findcountry.setChecked(FindCountry)

        self.ui.maxcpuusage.setValue(CPUsupport)
        CPUspeed = (CPUsupport/100-1)/-1
        self.webView.setUrl(QtCore.QUrl("https://j0113.github.io/ProxyHuntr/support.html?speed=" + str(CPUspeed)))

        sources=[line.strip() for line in open('sources.txt')]
        for url in sources:
            self.ui.sourcestext.appendPlainText(url)
            pass
        self.ui.stopbox.hide()
        pass

    def updatesources(self):
        sources = self.ui.sourcestext.toPlainText()
        with open("sources.txt", 'w+') as f:
            f.write(sources)
        self.logger("Updated Sources!")
        pass

    def ExportProxies(self):
        ExElite = self.ui.ExElite.isChecked()
        ExAnonymous = self.ui.ExAnonymous.isChecked()
        ExTransparent = self.ui.ExTransparent.isChecked()

        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getSaveFileName(self,"Choose were to save the proxies","","All Files (*);;Text Files (*.txt)", options=options)
        if fileName:
            if os.path.isfile("temp/Transparent.txt"):
                TransparentProxies=[line.strip() for line in open("temp/Transparent.txt")]
            else:
                TransparentProxies=[]
            if os.path.isfile("temp/Anonymous.txt"):
                AnonymousProxies=[line.strip() for line in open("temp/Anonymous.txt")]
            else:
                AnonymousProxies=[]
            if os.path.isfile("temp/Elite.txt"):
                EliteProxies=[line.strip() for line in open("temp/Elite.txt")]
            else:
                EliteProxies=[]
            with open((fileName), "w+") as f:
                f.write("")
            if ExElite:
                for proxy in EliteProxies:
                    out = open((fileName), "a")
                    out.write(proxy + "\n")
                    out.close
            if ExAnonymous:
                for proxy in AnonymousProxies:
                    out = open((fileName), "a")
                    out.write(proxy + "\n")
                    out.close
            if ExTransparent:
                for proxy in TransparentProxies:
                    out = open((fileName), "a")
                    out.write(proxy + "\n")
                    out.close
            self.logger("Proxies Exported!")
        pass

    def logger(self,msg):
        print(msg)
        self.ui.logger.appendPlainText(msg)
        pass


app = QApplication(sys.argv)
window = ProxyHuntrGUI()
window.show()
sys.exit(app.exec_())
