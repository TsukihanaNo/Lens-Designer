from PySide2 import QtCore, QtGui, QtWidgets
import time, math

class RenderAreaXH(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.label = QtWidgets.QLabel()
        self.parent=parent
        #canvas = QtGui.QPixmap(400,300)
        #self.label.setPixmap(canvas)
        self.height = parent.height-150
        # self.width = parent.geometry().width()
        self.scale =1.0
        self.offsetx =50
        self.offsety = 50
        self.xrange = 300
        self.yrange = 150
        self.width = self.xrange*12+100

        self.divergenceAngle=float(parent.lineDivergence.text())
        self.sourceHeight=float(parent.lineHeight.text())*12
        self.lostMod = float(parent.lineLostMod.text())
        self.lensInfo = []
        self.distanceLuxListMain=[]
        #self.setStyleSheet("background:#38285c")
        self.setStyleSheet("background:gray")
        self.setAutoFillBackground(True)
        self.setWindowTitle("Drawing")
        self.setGeometry(0,0,self.width*self.scale,self.height*self.scale)
        self.show()
        
    def paintEvent(self,event):
        painter = QtGui.QPainter(self)
        
        #painter.begin(self)
        painter.scale(self.scale, self.scale)

        pen = QtGui.QPen(QtCore.Qt.white,2)
        painter.setPen(pen)

        #draw axis
        point1 = QtCore.QPointF(self.offsetx, self.height-self.offsety)
        point2 = QtCore.QPointF(self.offsetx, self.height-self.offsety-self.sourceHeight)
        line1 = QtCore.QLineF(point1, point2)
        painter.drawLine(line1)

        point1 = QtCore.QPointF(self.offsetx, self.height-self.offsety)
        point2 = QtCore.QPointF(self.width-self.offsetx, self.height-self.offsety)
        line1 = QtCore.QLineF(point1, point2)
        painter.drawLine(line1)


        #draw markers
        for i in range(self.xrange*12+1):
            if i%(25*12)==0:
                painter.drawLine(self.offsetx+i,self.height-self.offsety-5,self.offsetx+i,self.height-self.offsety+10)
                painter.drawText(QtCore.QPointF(self.offsetx+(i)-15, self.height-self.offsety+30),str(i/12))

        #draw light source
        pen.setColor(QtCore.Qt.yellow)
        painter.setPen(pen)
        painter.setBrush(QtCore.Qt.yellow)
        painter.drawEllipse(self.offsetx-5,self.height-self.offsety-self.sourceHeight-10,10,10)

        #draw red horizontal ref
        pen.setColor(QtCore.Qt.red)
        pen.setStyle(QtCore.Qt.DotLine)
        painter.setPen(pen)
        point1 = QtCore.QPointF(self.offsetx, self.height-self.offsety-self.sourceHeight-5)
        point2 = QtCore.QPointF(self.offsetx+(12*self.xrange), self.height-self.offsety-self.sourceHeight-5)
        line1 = QtCore.QLineF(point1, point2)
        painter.drawLine(line1)

        text = "Output:\n"
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

                pen.setColor(QtGui.QColor(index*30,0,index*30,255*(output/100)))
                pen.setStyle(QtCore.Qt.SolidLine)
                painter.setPen(pen)

                if exitAngle>0:
                    distancex=(self.sourceHeight/math.tan(math.radians(exitAngle)))
                else:
                    distancex=self.xrange*12
                distancex1=math.tan(math.radians(beamAngle))*distancex
                
                #primary light
                point1 = QtCore.QPointF(self.offsetx, self.height-self.offsety-self.sourceHeight-5)
                if exitAngle>0:
                    point2 = QtCore.QPointF(self.offsetx+(distancex), self.height-self.offsety)
                else:
                    point2 = QtCore.QPointF(self.offsetx+(distancex), self.height-self.offsety-self.sourceHeight-5)
                line1 = QtCore.QLineF(point1, point2)
                painter.drawLine(line1)
                pointprimary = point2
                #lumens requirements (lumens=lux*D^2 where D is the hypotenus)
                hypo = math.sqrt((point2.x()-point1.x())**2+(point2.y()-point1.y())**2)
                hypo = (hypo/12)/3.281
                distancex1 = (distancex1/12)/3.281
                hypoy = math.tan(math.radians(self.divergenceAngle))*hypo
                lux = lumens /((hypoy*distancex1*4))
                lux = lux * (1-self.lostMod/100)
                lux = lux * output/100
                text = text + "primary lux: " + str(distancex/12) + " ft.  : " + str(lux) + " lux\n"

                if self.divergenceAngle>0:
                    #divergence light a
                    pen.setColor(QtGui.QColor(index*30,0,index*30,255*(output/100)))
                    pen.setStyle(QtCore.Qt.DotLine)
                    painter.setPen(pen)

                    angle = 90-exitAngle-self.divergenceAngle
                    distance = math.tan(math.radians(angle))*self.sourceHeight
                    distancex1 = math.tan(math.radians(beamAngle))*distance
                    distancex1 = (distancex1/12)/3.281
                    point1 = QtCore.QPointF(self.offsetx, self.height-self.offsety-self.sourceHeight-5)
                    point2 = QtCore.QPointF(self.offsetx+distance,self.height-self.offsety)
                    line1 = QtCore.QLineF(point1, point2)
                    painter.drawLine(line1)
                    
                    pointa = point2

                    painter.drawLine(self.offsetx+distance,self.height-self.sourceHeight-(100+index*10),self.offsetx+distance,self.height-self.offsety)
                    painter.drawText(QtCore.QPointF(self.offsetx+distance-15, self.height-self.sourceHeight-(110+index*15)),str(distance/12))
                    
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
                        painter.drawLine(line1)

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
                        painter.drawLine(line1)
                    
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
                    
                    painter.drawLine(self.offsetx+distance,self.height-self.sourceHeight-(150+index*10),self.offsetx+distance,self.height-self.offsety)
                    painter.drawText(QtCore.QPointF(self.offsetx+distance-15, self.height-self.sourceHeight-(160+index*15)),str(distance/12))
                index+=1
                self.distanceLuxListMain.append(distanceLuxListLens)
            self.parent.textOutput.setPlainText(text)
        painter.end()        
        
        
    def wheelEvent(self, event):
        modifiers = QtWidgets.QApplication.keyboardModifiers()
        if modifiers == QtCore.Qt.ControlModifier:
            if self.scale+event.delta()/240>=1:
                self.scale+=event.delta()/240
            else:
                self.scale=1

            self.resize(self.width*self.scale, self.height*self.scale)
            self.parent.labelRenderXH.setText("Render Area (zoom: " + str(self.scale)+"x)")
            self.update()
            
            
class RenderAreaXY(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.label = QtWidgets.QLabel()
        self.parent=parent
        #canvas = QtGui.QPixmap(400,300)
        #self.label.setPixmap(canvas)
        # self.width = parent.geometry().width()
        self.scale =0.5
        self.offsetx = 50
        self.offsety = 50
        self.xrange = 600
        self.yrange = 300
        #self.height = self.yrange*12+100
        self.width = self.xrange*12+100
        self.height=self.yrange*12+100
        self.setMinimumSize(self.width*self.scale,self.height*self.scale)
        self.divergenceAngle=float(parent.lineDivergence.text())
        self.sourceHeight=float(parent.lineHeight.text())*12
        self.lostMod = float(parent.lineLostMod.text())
        self.lensInfo = []
        #self.setStyleSheet("background:#38285c")
        self.setStyleSheet("background:gray")
        self.setAutoFillBackground(True)
        self.setWindowTitle("Drawing")
        self.setGeometry(0,0,self.width*self.scale,self.height*self.scale)
        self.show()
        
    def paintEvent(self,event):
        painter = QtGui.QPainter(self)
        
        #painter.begin(self)
        painter.scale(self.scale, self.scale)

        pen = QtGui.QPen(QtCore.Qt.white,2)
        painter.setPen(pen)

        #draw axis
        #y
        point1 = QtCore.QPointF(self.offsetx+((self.xrange/2)*12), self.height-self.offsety)
        point2 = QtCore.QPointF(self.offsetx+((self.xrange/2)*12), self.height-self.offsety-self.yrange*12)
        line1 = QtCore.QLineF(point1, point2)
        painter.drawLine(line1)
        #x
        point1 = QtCore.QPointF(self.offsetx, self.height-self.offsety)
        point2 = QtCore.QPointF(self.width-self.offsetx, self.height-self.offsety)
        line1 = QtCore.QLineF(point1, point2)
        painter.drawLine(line1)


        #draw markers
        #x
        for i in range((int(self.xrange/2))*12+1):
            if i%(25*12)==0:
                painter.drawLine(self.offsetx+((12*self.xrange)/2)+i,self.height-self.offsety-5,self.offsetx+((12*self.xrange)/2)+i,self.height-self.offsety+10)
                painter.drawText(QtCore.QPointF(self.offsetx+((12*self.xrange)/2)+(i)-15, self.height-self.offsety+30),str(i/12))
        for i in range((int(self.xrange/2))*12+1):
            if i%(25*12)==0 and i!=0:
                painter.drawLine(self.offsetx+((12*self.xrange)/2)-i,self.height-self.offsety-5,self.offsetx+((12*self.xrange)/2)-i,self.height-self.offsety+10)
                painter.drawText(QtCore.QPointF(self.offsetx+((12*self.xrange)/2)-(i)-15, self.height-self.offsety+30),str(i/12))
        #y
        for i in range((int(self.yrange))*12+1):
            if i%(25*12)==0 and i!=0:
                painter.drawLine(self.offsetx+((12*self.xrange)/2)-5,self.height-self.offsety-i,self.offsetx+((12*self.xrange)/2)+5,self.height-self.offsety-i)
                painter.drawText(QtCore.QPointF(self.offsetx+((12*self.xrange)/2)+10, self.height-self.offsety-i+10),str(i/12))


        #draw light source
        pen.setColor(QtCore.Qt.yellow)
        painter.setPen(pen)
        painter.setBrush(QtCore.Qt.yellow)
        painter.drawEllipse(self.offsetx+(12*(self.xrange/2))-5,self.height-self.offsety-5,10,10)

        text = "Output:\n"

        #iterate through lens list
        index=1
        for item in self.lensInfo:
            if item[5]==QtCore.Qt.CheckState.Checked:
                exitAngle = item[0]
                lumens = item[1]
                output = item[2]
                beamAngle = item[3]
                fieldAngle = item[4]

                pen.setColor(QtGui.QColor(index*30,0,index*30,255*(output/100)))
                pen.setStyle(QtCore.Qt.SolidLine)
                painter.setPen(pen)

                #convert distanceX to inches
                if exitAngle>0:
                    distancey=(self.sourceHeight/math.tan(math.radians(exitAngle)))
                else:
                    distancey = self.yrange*12
                distancex=math.tan(math.radians(beamAngle))*distancey
                
                #primary light
                #pointp1 = QtCore.QPointF(self.offsetx+(self.xrange/2)*12, self.height-self.offsety)
                pointp1 = QtCore.QPointF(self.offsetx+(self.xrange/2)*12+(distancex), self.height-self.offsety-distancey)
                pointp2 = QtCore.QPointF(self.offsetx+(self.xrange/2)*12-(distancex), self.height-self.offsety-distancey)
                #line1 = QtCore.QLineF(point1, point2)
                #painter.drawLine(line1)
                
                #lumens requirements (lumens=lux*D^2 where D is the hypotenus)
                hypo = math.sqrt((point2.x()-point1.x())**2+(point2.y()-point1.y())**2)
                #convert to feet then meters
                hypo = (hypo/12)/3.281
                hypoy = math.tan(math.radians(self.divergenceAngle))*hypo
                lux = lumens /(2*(hypoy**2))
                lux = lux * (1-self.lostMod/100)
                lux = lux * output/100
                #text = text + "primary lux: " + str(distancex/12) + " ft.  : " + str(lux) + " lux\n"
                if self.divergenceAngle>0:
                    #divergence light a
                    pen.setColor(QtGui.QColor(index*30,0,index*30,255*(output/100)))
                    pen.setStyle(QtCore.Qt.DotLine)
                    painter.setPen(pen)

                    angle = 90-exitAngle-self.divergenceAngle
                    distancey = math.tan(math.radians(angle))*self.sourceHeight
                    distancex = math.tan(math.radians(beamAngle))*distancey
                    
                    #side1
                    pointo = QtCore.QPointF(self.offsetx+(self.xrange/2)*12, self.height-self.offsety-distancey)
                    pointa1 = QtCore.QPointF(self.offsetx+(self.xrange/2)*12+distancex,self.height-self.offsety-distancey)
                    
                    #side2
                    pointo = QtCore.QPointF(self.offsetx+(self.xrange/2)*12, self.height-self.offsety-distancey)
                    pointa2 = QtCore.QPointF(self.offsetx+(self.xrange/2)*12-distancex,self.height-self.offsety-distancey)

                    #painter.drawLine(self.offsetx+distancex,self.height-self.sourceHeight-(100+index*10),self.offsetx+distancex,self.height-self.offsety)
                    #painter.drawText(QtCore.QPointF(self.offsetx+distancex-15, self.height-self.sourceHeight-(110+index*15)),str(distance/12))

                    #text = text + "div a lux: " + str(distance/12) + " ft.  : " + str(lux) + " lux\n"

                    #divergence light b
                    if self.divergenceAngle>exitAngle:
                        angle = self.divergenceAngle - exitAngle
                        distancey =self.xrange*12
                        distancex = math.tan(math.radians(beamAngle))*distancey
                        
                        #side1
                        pointo = QtCore.QPointF(self.offsetx+(self.xrange/2)*12, self.height-self.offsety-distancey)
                        pointb1 = QtCore.QPointF(self.offsetx+(self.xrange/2)*12+distancex,self.height-self.offsety- distancey)
                        #side2
                        pointo = QtCore.QPointF(self.offsetx+(self.xrange/2)*12, self.height-self.offsety-distancey)
                        pointb2 = QtCore.QPointF(self.offsetx+(self.xrange/2)*12-distancex,self.height-self.offsety- distancey)
                    else:
                        angle = exitAngle - self.divergenceAngle
                        if angle ==0:
                            distancey =self.xrange*12
                            distancex = math.tan(math.radians(beamAngle))*distancey
                        else:
                            distancey = self.sourceHeight/math.tan(math.radians(angle))
                            distancex = math.tan(math.radians(beamAngle))*distancey
                        #side1
                        pointo = QtCore.QPointF(self.offsetx+(self.xrange/2)*12, self.height-self.offsety-distancey)
                        pointb1 = QtCore.QPointF(self.offsetx+(self.xrange/2)*12+distancex,self.height-self.offsety- distancey)
                        #side2
                        pointo = QtCore.QPointF(self.offsetx+(self.xrange/2)*12, self.height-self.offsety-distancey)
                        pointb2 = QtCore.QPointF(self.offsetx+(self.xrange/2)*12-distancex,self.height-self.offsety- distancey)


                    painter.setBrush(QtGui.QColor(index*30,0,index*30,255*(output/100)))
                    gradient =QtGui.QLinearGradient(self.offsetx+(self.xrange/2)*12,pointa2.y(),self.offsetx+(self.xrange/2)*12,pointb2.y())
                    gradient.setColorAt(0,QtGui.QColor(index*30,0,index*30,200))
                    gradient.setColorAt(1,QtGui.QColor(index*30,0,index*30,100))

                    painter.setBrush(gradient)
                    polygon = QtGui.QPolygonF([pointa1,pointb1,pointb2,pointa2])
                    path = QtGui.QPainterPath()
                    path.addPolygon(polygon)
                    
                    painter.drawPath(path)
                
                #painter.drawLine(self.offsetx+distance,self.height-self.sourceHeight-(150+index*10),self.offsetx+distance,self.height-self.offsety)
                #painter.drawText(QtCore.QPointF(self.offsetx+distance-15, self.height-self.sourceHeight-(160+index*15)),str(distance/12))
            index+=1
            # self.parent.labelOutput.setText(text)
        painter.end()           
        
    def wheelEvent(self, event):
        modifiers = QtWidgets.QApplication.keyboardModifiers()
        if modifiers == QtCore.Qt.ControlModifier:
            if self.scale+event.delta()/240>=0.5:
                self.scale+=event.delta()/240
            else:
                self.scale=0.5

            self.resize(self.width*self.scale, self.height*self.scale)
            self.parent.labelRenderXY.setText("Render Area XY (zoom: " + str(self.scale)+"x)")
            self.update()
            
class RenderAreaLux(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.label = QtWidgets.QLabel()
        self.parent=parent
        #canvas = QtGui.QPixmap(400,300)
        #self.label.setPixmap(canvas)
        # self.width = parent.geometry().width()
        self.scale =1.0
        self.offsetx =50
        self.offsety = 50
        self.xrange = 300
        self.yrange = 300
        self.width = self.xrange*2+100
        self.height = self.yrange*2+100

        self.luxDistance=[]
        #self.setStyleSheet("background:#38285c")
        self.setStyleSheet("background:gray")
        self.setAutoFillBackground(True)
        self.setWindowTitle("Lux Graph")
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setGeometry(0,0,self.width*self.scale,self.height*self.scale)
        #self.center()
        self.show()
        
    def paintEvent(self,event):
        painter = QtGui.QPainter(self)
        
        #painter.begin(self)
        painter.scale(self.scale, self.scale)

        pen = QtGui.QPen(QtCore.Qt.white,2)
        painter.setPen(pen)

        #draw axis
        point1 = QtCore.QPointF(self.offsetx, self.height-self.offsety-self.yrange*2)
        point2 = QtCore.QPointF(self.offsetx, self.height-self.offsety)
        line1 = QtCore.QLineF(point1, point2)
        painter.drawLine(line1)

        point1 = QtCore.QPointF(self.offsetx, self.height-self.offsety)
        point2 = QtCore.QPointF(self.width-self.offsetx, self.height-self.offsety)
        line1 = QtCore.QLineF(point1, point2)
        painter.drawLine(line1)


        #draw markers
        #x axis
        for i in range(self.xrange*2+1):
            if i%(50)==0:
                painter.drawLine(self.offsetx+i,self.height-self.offsety-5,self.offsetx+i,self.height-self.offsety+10)
                painter.drawText(QtCore.QPointF(self.offsetx+(i)-15, self.height-self.offsety+30),str(i/2))
        painter.drawText(QtCore.QPointF(self.width/2, self.height-5),"Distance (ft.)")
        #yaxis
        for i in range(self.yrange*2+1):
            if i%(50)==0:
                painter.drawLine(self.offsetx-5,self.height-self.offsety-i,self.offsetx+5,self.height-self.offsety-i)
                painter.drawText(QtCore.QPointF(self.offsetx-40, self.height-self.offsety-i+5),str(i/2))
        painter.drawText(QtCore.QPointF(5, 25),"Lux (lm/m^2)")
        #draw points
        for item in self.luxDistance:
            painter.drawPoint(item[0]*2+self.offsetx, self.height-self.offsety-item[1]*2)
        
        painter.end()      
                                      
                        
        
    def wheelEvent(self, event):
        modifiers = QtWidgets.QApplication.keyboardModifiers()
        if modifiers == QtCore.Qt.ControlModifier:
            if self.scale+event.delta()/240>=1:
                self.scale+=event.delta()/240
            else:
                self.scale=1

            self.resize(self.width*self.scale, self.height*self.scale)
            self.parent.labelRenderXH.setText("Render Area (zoom: " + str(self.scale)+"x)")
            self.update()

