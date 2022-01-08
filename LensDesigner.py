from PySide2 import QtCore, QtGui, QtWidgets
import time, math
from RenderArea import *
from TableWidget import *


class Scroller(QtWidgets.QScrollArea):
    def __init__(self, parent=None):
        super().__init__()
                
    # def wheelEvent(self, event):
    #     modifiers = QtWidgets.QApplication.keyboardModifiers()
    #     if modifiers == QtCore.Qt.ControlModifier:
    #         event.ignore()
        

class LenseDesigner(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        
        self.height=1000
        self.width=1920
        #input parameters
        vboxlayoutInput = QtWidgets.QVBoxLayout()
        self.labelHeight = QtWidgets.QLabel("Height (ft):")
        self.lineHeight = QtWidgets.QLineEdit("8")

        self.labelDivergence = QtWidgets.QLabel("Divergence Angle")
        self.lineDivergence = QtWidgets.QLineEdit("8")

        self.labelLostMod = QtWidgets.QLabel("Attenuation Modifier (%)")
        self.lineLostMod = QtWidgets.QLineEdit("0")

        self.labelLensInfo = QtWidgets.QLabel("Lens Info")
        
        #self.tableLensInfo = QtWidgets.QTableWidget(5, 6)
        self.tableLensInfo = TableWdiget(1,6,self)
        self.tableLensInfo.setHorizontalHeaderItem(0, QtWidgets.QTableWidgetItem("Exit Angle"))
        self.tableLensInfo.setHorizontalHeaderItem(1, QtWidgets.QTableWidgetItem("Source Lumens"))
        self.tableLensInfo.setHorizontalHeaderItem(2,QtWidgets.QTableWidgetItem("Output %"))
        self.tableLensInfo.setHorizontalHeaderItem(3, QtWidgets.QTableWidgetItem("Beam Angle"))
        self.tableLensInfo.setHorizontalHeaderItem(4, QtWidgets.QTableWidgetItem("Field Angle"))
        self.tableLensInfo.setHorizontalHeaderItem(5, QtWidgets.QTableWidgetItem("Show"))
        self.tableLensInfo.setColumnWidth(5, 25)
        
        for x in range(self.tableLensInfo.rowCount()):
            checkbox = QtWidgets.QTableWidgetItem()
            checkbox.setFlags(QtCore.Qt.ItemIsUserCheckable|QtCore.Qt.ItemIsEnabled)
            checkbox.setCheckState(QtCore.Qt.Checked)
            self.tableLensInfo.setItem(x, 5, checkbox)
        
        self.button = QtWidgets.QPushButton("Render")
        self.button.clicked.connect(self.Render)
        
        self.button_save = QtWidgets.QPushButton("Save Graphs")
        self.button_save.clicked.connect(self.exportImage)
        
        self.tab = QtWidgets.QTabWidget(self)
        

        self.textOutput = QtWidgets.QTextEdit("Output:")
        self.textLux = QtWidgets.QTextEdit("Distance : Lux")
        
        self.tab.addTab(self.textOutput, "Output")
        self.tab.addTab(self.textLux, "Lux")
        container = QtWidgets.QWidget()
        container.setLayout(vboxlayoutInput)
        container.setMaximumWidth(450)
        
        
        vboxlayoutInput.addWidget(self.labelHeight)
        vboxlayoutInput.addWidget(self.lineHeight)
        vboxlayoutInput.addWidget(self.labelDivergence)
        vboxlayoutInput.addWidget(self.lineDivergence)
        vboxlayoutInput.addWidget(self.labelLostMod)
        vboxlayoutInput.addWidget(self.lineLostMod)
        vboxlayoutInput.addWidget(self.labelLensInfo)
        vboxlayoutInput.addWidget(self.tableLensInfo)
        vboxlayoutInput.addWidget(self.button)
        vboxlayoutInput.addWidget(self.button_save)
        vboxlayoutInput.addWidget(self.tab)
        #vboxlayoutInput.addWidget(self.textOutput)

        self.tabRender = QtWidgets.QTabWidget(self)
        
        self.scrollareaXH = QtWidgets.QScrollArea(self)
        self.scrollareaXY = QtWidgets.QScrollArea(self)
        self.scrollareaLux = QtWidgets.QScrollArea(self)
        
        self.labelRenderXY = QtWidgets.QLabel("Render Area XY (zoom: 0.5x)")
        self.labelRenderXH = QtWidgets.QLabel("Render Area XH (zoom: 1.0x)")
        
        self.renderAreaLux = RenderAreaLux(self)
        self.scrollareaLux.setWidget(self.renderAreaLux)

        vbox1 = QtWidgets.QVBoxLayout()
        vbox2 = QtWidgets.QVBoxLayout()

        self.renderAreaXH = RenderAreaXH(self)
        self.renderAreaXY = RenderAreaXY(self)
        self.scrollareaXH.setWidget(self.renderAreaXH)
        self.scrollareaXY.setWidget(self.renderAreaXY)

        vbox1.addWidget(self.labelRenderXY)
        vbox1.addWidget(self.scrollareaXY)
        vbox2.addWidget(self.labelRenderXH)
        vbox2.addWidget(self.scrollareaXH)

        widget1 = QtWidgets.QWidget()
        widget1.setLayout(vbox1)

        widget2 = QtWidgets.QWidget()
        widget2.setLayout(vbox2)

        self.tabRender.addTab(widget1,"Plot XH")
        self.tabRender.addTab(widget2,"Plot XY")
        self.tabRender.addTab(self.scrollareaLux,"AreaLux")


        self.scrollareaXY.verticalScrollBar().setSliderPosition(self.scrollareaXY.verticalScrollBar().maximum())
        self.scrollareaXH.verticalScrollBar().setSliderPosition(self.scrollareaXH.verticalScrollBar().maximum())
        
        #main layout
        hboxlayoutMain = QtWidgets.QHBoxLayout(self)
        hboxlayoutMain.addWidget(container)
        hboxlayoutMain.addWidget(self.tabRender)
        self.setGeometry(0, 0, self.width, self.height)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.center()
        self.setWindowTitle('Lense Designer')
        self.show()
        
    def center(self):
        window = self.window()
        window.setGeometry(
            QtWidgets.QStyle.alignedRect(
            QtCore.Qt.LeftToRight,
            QtCore.Qt.AlignCenter,
            window.size(),
            QtGui.QGuiApplication.primaryScreen().availableGeometry(),
        ),
    )

        
    def Render(self):
        self.renderAreaXH.sourceHeight=float(self.lineHeight.text())*12
        self.renderAreaXH.divergenceAngle=float(self.lineDivergence.text())
        self.renderAreaXH.lostMod = float(self.lineLostMod.text())
        self.renderAreaXH.lensInfo = self.GenerateLensInfo()
        
        self.renderAreaXY.sourceHeight=float(self.lineHeight.text())*12
        self.renderAreaXY.divergenceAngle=float(self.lineDivergence.text())
        self.renderAreaXY.lostMod = float(self.lineLostMod.text())
        self.renderAreaXY.lensInfo = self.GenerateLensInfo()
        
        self.renderAreaLux.luxDistance = self.GenerateLuxTable(self.renderAreaXH.distanceLuxListMain)
        
        self.printLux(self.renderAreaLux.luxDistance)
        
        self.renderAreaXH.update()
        self.renderAreaXY.update()
        self.renderAreaLux.update()
        
    def exportImage(self):
        p = QtGui.QPixmap.grabWidget(self.renderAreaXY)
        p.save("renderareaXY.jpg","jpg")
        p = QtGui.QPixmap.grabWidget(self.renderAreaXH)
        p.save("renderareaXH.jpg","jpg")
        p = QtGui.QPixmap.grabWidget(self.renderAreaLux)
        p.save("renderareaLux.jpg","jpg") 
    
    def GenerateLensInfo(self):
        lensInfo=[]
        for x in range(self.tableLensInfo.rowCount()):
            if self.tableLensInfo.item(x, 0)!= None and self.tableLensInfo.item(x, 1)!=None:
                lensInfo.append((float(self.tableLensInfo.item(x,0).text()),float(self.tableLensInfo.item(x,1).text()),float(self.tableLensInfo.item(x,2).text()),float(self.tableLensInfo.item(x,3).text()),float(self.tableLensInfo.item(x,4).text()),self.tableLensInfo.item(x, 5).checkState()))
        return lensInfo

    def GenerateRaysInfo(self):
        #XH[(diva,lux),(primary,lux),(divb,lux)]
        #xY[(diva,primary,divb)]
        self.distanceLuxListMain=[]
        index = 1
        #iterate through lens list
        for item in self.lensInfo:
            if item[5]==QtCore.Qt.CheckState.Checked:
                distanceLuxListLens=[]
                exitAngle = item[0]
                lumens = item[1]
                output = item[2]
                beamAngle = item[3]

                if exitAngle>0:
                    primaryx=(self.sourceHeight/math.tan(math.radians(exitAngle)))
                else:
                    primaryx=self.xrange*12
                distancex1=math.tan(math.radians(beamAngle))*primaryx
                
                #primary light
                point1 = QtCore.QPointF(0, self.height-self.offsety-self.sourceHeight-5)
                if exitAngle>0:
                    point2 = QtCore.QPointF((primaryx), self.height)
                else:
                    point2 = QtCore.QPointF(self.offsetx+([primaryx]), self.height-self.offsety-self.sourceHeight-5)
                line1 = QtCore.QLineF(point1, point2)
                pointprimary = point2
                #lumens requirements (lumens=lux*D^2 where D is the hypotenus)
                hypo = math.sqrt((point2.x()-point1.x())**2+(point2.y()-point1.y())**2)
                hypo = (hypo/12)/3.281
                distancex1 = (distancex1/12)/3.281
                hypoy = math.tan(math.radians(self.divergenceAngle))*hypo
                lux = lumens /((hypoy*distancex1*4))
                lux = lux * (1-self.lostMod/100)
                lux = lux * output/100
                text = text + "primary lux: " + str(primaryx/12) + " ft.  : " + str(lux) + " lux\n"

                if self.divergenceAngle>0:
                    #divergence light a

                    angle = 90-exitAngle-self.divergenceAngle
                    distance = math.tan(math.radians(angle))*self.sourceHeight
                    distancex1 = math.tan(math.radians(beamAngle))*distance
                    distancex1 = (distancex1/12)/3.281
                    point1 = QtCore.QPointF(self.offsetx, self.height-self.offsety-self.sourceHeight-5)
                    point2 = QtCore.QPointF(self.offsetx+distance,self.height-self.offsety)
                    line1 = QtCore.QLineF(point1, point2)
                    
                    pointa = point2
                    
                    hypo = math.sqrt((point2.x()-point1.x())**2+(point2.y()-point1.y())**2)
                    #convert to feet then meters
                    hypo = (hypo/12)/3.281
                    hypoy = math.sin(math.radians(self.divergenceAngle))*hypo
                    lux = lumens /((hypoy*distancex1*4))
                    lux = lux * (1-self.lostMod/100)
                    lux = lux * output/100

                    text = text + "div a lux: " + str(distance/12) + " ft.  : " + str(lux) + " lux\n"
                    text = text + "Lux for Distances Min to Primary Ray:\n"
                    #calculate lux at 1 feet increments from Div A to Primary
                    for x in range(int((pointprimary.x()-self.offsetx)/12)-int((pointa.x()-self.offsetx)/12)+1):
                        newx = int((pointa.x()-self.offsetx)/12)+x
                        theta_s = math.degrees(math.atan(newx/(self.sourceHeight/12)))
                        theta_a1 = 90-exitAngle - theta_s
                        length = math.sqrt(newx**2+(self.sourceHeight/12)**2)
                        y1 = length*math.tan(math.radians(theta_a1))
                        ytotal = y1 + math.tan(math.radians(self.divergenceAngle-theta_a1))*length
                        distancex1 = math.tan(math.radians(beamAngle))*(newx)
                        distancex1 = (distancex1)/3.281
                        ytotal = (ytotal)/3.281
                        lux = lumens /((ytotal*distancex1*4))
                        lux = lux * (1-self.lostMod/100)
                        lux = lux * output/100
                        text = text + " - " + str((newx)) + " ft.  : " + str(lux) + " lux\n"
                        distanceLuxListLens.append([newx,lux])

                    #divergence light b
                    if self.divergenceAngle>exitAngle:
                        angle = self.divergenceAngle - exitAngle
                        distance=self.xrange*12
                        height = math.tan(math.radians(angle))*distance
                        point1 = QtCore.QPointF(self.offsetx, self.height-self.offsety-self.sourceHeight-5)
                        point2 = QtCore.QPointF(self.offsetx+distance,self.height-self.offsety- height)
                        line1 = QtCore.QLineF(point1, point2)

                    else:
                        angle = exitAngle - self.divergenceAngle
                        if angle ==0:
                            distance = self.xrange*12
                            point1 = QtCore.QPointF(self.offsetx, self.height-self.offsety-self.sourceHeight-5)
                            point2 = QtCore.QPointF(self.offsetx+(distance),self.height-self.offsety-self.sourceHeight-5)
                        else:
                            distance = self.sourceHeight/math.tan(math.radians(angle))
                            point1 = QtCore.QPointF(self.offsetx, self.height-self.offsety-self.sourceHeight-5)
                            point2 = QtCore.QPointF(self.offsetx+(distance),self.height-self.offsety)
                        line1 = QtCore.QLineF(point1, point2)
                    
                    pointb = point2
                    
                    hypo = math.sqrt((point2.x()-point1.x())**2+(point2.y()-point1.y())**2)
                    #convert to feet then meters
                    hypo = (hypo/12)/3.281
                    distancex1 = math.tan(math.radians(beamAngle))*distance
                    distancex1 = (distancex1/12)/3.281
                    hypoy = math.sin(math.radians(self.divergenceAngle))*hypo
                    lux = lumens /((hypoy*distancex1*4))
                    lux = lux * (1-self.lostMod/100)
                    lux = lux * output/100
                    
                    text = text + "div b lux: " + str(distance/12) + " ft.  : " + str(lux) + " lux\n"
                    
                    text = text + "Lux for Distances Primary ray to Max:\n"
                    #calculate lux at 1 feet increments from Primary to Div B
                    for x in range(int((pointb.x()-self.offsetx)/12)-int((pointprimary.x()-self.offsetx)/12)+1):
                        #theta_s = math.degrees(math.atan(((pointa.x()-self.offsetx)+x*12)/self.sourceHeight))
                        newx = int((pointprimary.x()-self.offsetx)/12)+x
                        theta_s = math.degrees(math.atan(newx/(self.sourceHeight/12)))
                        theta_b = math.degrees(math.atan(self.sourceHeight/(pointb.x()-self.offsetx)))
                        theta_b1 = 90- theta_s - theta_b
                        length = math.sqrt(newx**2+(self.sourceHeight/12)**2)
                        y1 = length*math.tan(math.radians(theta_b1))
                        ytotal = y1 + math.tan(math.radians(self.divergenceAngle-theta_b1))*length
                        distancex1 = math.tan(math.radians(beamAngle))*(newx)
                        distancex1 = distancex1/3.281
                        ytotal = ytotal/3.281
                        lux = lumens /((ytotal*distancex1*4))
                        lux = lux * (1-self.lostMod/100)
                        lux = lux * output/100
                        text = text + " - " + str(newx) + " ft.  : " + str(lux) + " lux\n"
                        if x>0:
                            distanceLuxListLens.append([newx,lux])
        pass
    
    def GenerateLuxTable(self,distanceLuxMain):
        distanceLux=[]
        table = distanceLuxMain
        for i in range(len(table)):
            for j in range(len(table[i])):
                if len(distanceLux)==0:
                    distanceLux.append(table[i][j])
                else:
                    for k in range(len(distanceLux)):
                        if table[i][j][0]==distanceLux[k][0]:
                            distanceLux[k][1] = distanceLux[k][1] + table[i][j][1]
                            break
                        if k == len(distanceLux)-1:
                            if table[i][j][0]!=distanceLux[k][0]:
                                distanceLux.append(table[i][j])
        return distanceLux
    
    def printLux(self,distanceLux):
        text = "Distance : Lux\n"
        for item in distanceLux:
            text = text + str(item[0]) + " : " + str(item[1]) +"\n"
        self.textLux.setPlainText(text)
            
if __name__ == "__main__":
    app = QtWidgets.QApplication()
    w = LenseDesigner()
    w.show()
    app.exec_()

