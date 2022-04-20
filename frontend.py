from PySide6 import QtCore, QtWidgets, QtGui
from backend.backend import Backend
from backend.backendErrors import *
import frontendConstants as cnts
import sys

global bkend, manEvents 
bkend = Backend()

class MyWidget(QtWidgets.QWidget):
    '''
    Inicial windows 
    contains the calendar and the buttons to change an event status
    '''
    def __init__(self):
        super().__init__()
        self.setup()
        
    def setup(self):
        self.Calendar = MyCalendar()
        self.Buttons = MyButtonsMain(self.Calendar)

        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.addWidget(self.Calendar)
        self.layout.addWidget(self.Buttons)
        self.setWindowTitle("Agenda")

class MyButtonsMain(QtWidgets.QWidget):
    '''
        Stores and controls all the buttons in the main Window
    '''
    def __init__(self, activated):
        super().__init__()
        self.act = activated
        self.drawMain()
        

    def drawMain(self):
        self.words = [cnts.SEEEDITEVENTS, cnts.ADDEVENTS, cnts.SAVESYSTEM, cnts.DELETELAST]
        self.buttons = [QtWidgets.QPushButton(self.words[i]) for i in range(len(self.words))] 
        self.layout = QtWidgets.QHBoxLayout(self)

        for i in range(len(self.buttons)):
            self.layout.addWidget(self.buttons[i])
            self.magic(self.buttons[i])

    @QtCore.Slot()
    def magic(self, button):
        if cnts.SEEEDITEVENTS == button.text():
            button.clicked.connect(self.act.SeeEditEvents)
        elif cnts.ADDEVENTS == button.text():
            button.clicked.connect(self.act.AddEvent)
        elif cnts.DELETELAST == button.text():
            button.clicked.connect(self.act.Undo)
        elif cnts.SAVESYSTEM == button.text():
            button.clicked.connect(self.SaveState)     

    def SaveState(self):
        try:    
            bkend.save()
            MyNotifications(cnts.SUCCESSSAVE, icon=QtWidgets.QMessageBox.Information, title=cnts.ACTIONOCOURED)
        except SavingError:
            MyNotifications(cnts.ERRORSAVING)

class ManageEvents:
    def showEvent(self, layout, functions, event):
        day, hour, current  = [int(i) for i in bkend.getEventDate(event).split("-")], [int(a) for a in bkend.getEventHour(event).split(":")], bkend.currentTime()
        functions[0].setMinimumDate(QtCore.QDate(current[0], current[1], current[2]))
        functions[0].setDateTime(QtCore.QDateTime(QtCore.QDate(day[0], day[1], day[2]), QtCore.QTime(hour[0], hour[1])))
        functions[0].setDisplayFormat("dd/MM/yyyy hh:mm")
        functions[1].setText(str(bkend.getEventPlace(event)))
        functions[2].setText(str(bkend.getEventMatter(event)))
        functions[3].setText(str(bkend.getEventSupperior(event)))
        functions[4].setText(str(bkend.getEventName(event)))
        functions[5].setChecked(bkend.getEventStatus(event))
        self.showFunct = functions

        layout.addRow(f"{cnts.LABELDATE}", functions[0])
        layout.addRow(f"{cnts.LABELFINNISHED}", functions[5])
        layout.addRow(f"{cnts.LABELPLACE}", functions[1])
        layout.addRow(f"{cnts.LABELMATTER}", functions[2])
        layout.addRow(f"{cnts.LABELSUPPERIOR}", functions[3])
        layout.addRow(f"{cnts.LABELNAME}", functions[4])

    def addEventForm(self, layout, functions, date):
        today, date = bkend.currentTime(), [int(i) for i in date.split("-")]
        functions[0].setMinimumDate(QtCore.QDate(today[0], today[1], today[2]))
        functions[0].setDate(QtCore.QDate(date[0], date[1], date[2]))
        functions[0].setDisplayFormat("dd/MM/yyyy hh:mm")
        self.addfunctions = functions

        layout.addRow(f"{cnts.LABELDATE}", functions[0])
        layout.addRow(f"{cnts.LABELPLACE}", functions[1])
        layout.addRow(f"{cnts.LABELMATTER}", functions[2])
        layout.addRow(f"{cnts.LABELSUPPERIOR}", functions[3])
        layout.addRow(f"{cnts.LABELNAME}", functions[4])

class SeeEditEventsForm(QtWidgets.QWidget):
    def __init__(self, event):
        super().__init__()
        self.ev = event
        self.window = QtWidgets.QMainWindow()
        self.layout = QtWidgets.QVBoxLayout()
        self.setWindowTitle(cnts.SEEEDITEVENTS)
        self.formLayout = QtWidgets.QFormLayout()
        self.showFunctions = [QtWidgets.QDateTimeEdit(), \
                                                QtWidgets.QTextEdit(), QtWidgets.QTextEdit(), \
                                                QtWidgets.QTextEdit(), QtWidgets.QTextEdit(), \
                                                QtWidgets.QCheckBox()]
        
        self.editButtons = [QtWidgets.QPushButton(i) for i in [cnts.DELETEEVENT, cnts.SAVEEVENT]]

        self.horizontalGroupBox = QtWidgets.QGroupBox(self.ev.getDate())

        manEvents.showEvent(self.formLayout, self.showFunctions, self.ev)

        self.horizontalGroupBox.setLayout(self.formLayout)

        for button in self.editButtons:
            self.formLayout.addRow(button)
            self.magic(button)
        self.layout.addWidget(self.horizontalGroupBox)

        self.setLayout(self.formLayout)

    @QtCore.Slot()
    def magic(self, button):
        if cnts.DELETEEVENT == button.text():
            button.clicked.connect(self.Remove)
        elif cnts.SAVEEVENT == button.text():
            button.clicked.connect(self.saveEvents)

    def saveEvents(self):
        dateSet = self.showFunctions[0].dateTime().toString(self.showFunctions[0].displayFormat())
        dateSet = dateSet.split(" ")
        dateSet[0] = "-".join(dateSet[0].split("/")[::-1])
        placeSet = self.showFunctions[1].toPlainText()
        matterSet = self.showFunctions[2].toPlainText()
        supperiorSet = self.showFunctions[3].toPlainText()
        nameSet = self.showFunctions[4].toPlainText()

        try:
            bkend.changeEvent(self.ev, date=dateSet[0], time=dateSet[1], place=placeSet, procN=matterSet, \
                                trib= supperiorSet, name= nameSet, status=self.showFunctions[5].isChecked(), id=self.ev.getId())
            date = dateSet[0].split("-")
            MyNotifications(f"{cnts.EVENTCHANGED} {date[2]}/{date[1]}/{date[0]} {dateSet[1]}", icon=QtWidgets.QMessageBox.Information, title=cnts.ACTIONOCOURED)
        
        except EventAlreadyExists:
            date = dateSet[0].split("-")
            MyNotifications(f"{cnts.EVENTEXISTS} {date[2]}/{date[1]}/{date[0]} {dateSet[1]}")


        except DateTimeError:
            date = dateSet[0].split("-")
            MyNotifications(f"{cnts.DATEERROR} {date[2]}/{date[1]}/{date[0]} {dateSet[1]}")

        except EventNotFound:
            date = dateSet[0].split("-")
            MyNotifications(f"{cnts.EVENTDELETED} {date[2]}/{date[1]}/{date[0]} {dateSet[1]}")

    def Remove(self):
        try:
            evn = bkend.removeEvent(self.ev)
            date = evn.getDate().split("-")
            MyNotifications(f"{cnts.DISPLAYREMOVEDEVENT} {date[2]}/{date[1]}/{date[0]} {evn.getHour()}", icon=QtWidgets.QMessageBox.Information, title=cnts.ACTIONOCOURED)
        
        except EventNotFound:
            MyNotifications(f"{cnts.NOEVENT}")

class AddEventsForm(QtWidgets.QWidget):
    def __init__(self, date):
        super().__init__()
        self.window = QtWidgets.QMainWindow()
        self.layout = QtWidgets.QVBoxLayout()
        self.setWindowTitle(cnts.ADDEVENT)
        self.formLayout = QtWidgets.QFormLayout()  
        self.horizontalGroupBox = QtWidgets.QGroupBox() 
        self.addFunctions = [QtWidgets.QDateTimeEdit(), \
                                                QtWidgets.QTextEdit(), QtWidgets.QTextEdit(), \
                                                QtWidgets.QTextEdit(), QtWidgets.QTextEdit(), \
                                                QtWidgets.QTextEdit()]  

        manEvents.addEventForm(self.formLayout, self.addFunctions, date)

        self.horizontalGroupBox.setLayout(self.formLayout)
        self.layout.addWidget(self.horizontalGroupBox)
        button = QtWidgets.QPushButton(cnts.ADDEVENT)
        self.formLayout.addRow(button)
        self.magic(button)
        self.setLayout(self.formLayout)
    
    def addEvent(self):
        dateSet = self.addFunctions[0].dateTime().toString(self.addFunctions[0].displayFormat())
        dateSet = dateSet.split(" ")
        dateSet[0] = "-".join(dateSet[0].split("/")[::-1])
        placeSet = self.addFunctions[1].toPlainText()
        matterSet = self.addFunctions[2].toPlainText()
        supperiorSet = self.addFunctions[3].toPlainText()
        nameSet = self.addFunctions[4].toPlainText()

        try:
            bkend.setEvent(date=dateSet[0], time=dateSet[1], place=placeSet, procN=matterSet, trib= supperiorSet, name= nameSet)
            date = dateSet[0].split("-")
            MyNotifications(f"{cnts.EVENTINSERTED} {dateSet[0]} {dateSet[1]}", icon=QtWidgets.QMessageBox.Information, title=cnts.ACTIONOCOURED)

        except DateTimeError:
            date = dateSet[0].split("-")
            MyNotifications(f"{cnts.DATEERROR} {date[2]}/{date[1]}/{date[0]}")

        except EventAlreadyExists:
            MyNotifications(f"{cnts.EVENTEXISTS}")

    @QtCore.Slot()
    def magic(self, button):
        if cnts.ADDEVENT == button.text():
            button.clicked.connect(self.addEvent)

class MyCalendar(QtWidgets.QWidget):
    '''
        Calendar widget shown in the main window
    '''
    def __init__(self):
        super().__init__()
        self.setup()

    def setup(self, initDate=(bkend.currentTime(), bkend.advanceTime(cnts.DASYTOSHOW))):
        self.layout = QtWidgets.QVBoxLayout(self)
        self.cal = QtWidgets.QCalendarWidget()
        self.layout.addWidget(self.cal)
        self.startTime = initDate[0]
        self.endTime =  initDate[1]
        self.cal.setDateRange(QtCore.QDate(initDate[0][0], initDate[0][1], initDate[0][2]),\
            QtCore.QDate(initDate[1][0], initDate[1][1], initDate[1][2]))
        self.cal.setGridVisible(True)
        self.cal.setNavigationBarVisible(True)
        self.windows = []

    def SeeEditEvents(self):
        try:  
            for event in bkend.getEventsByDate(self.cal.selectedDate().toString(QtCore.Qt.ISODate)):  
                wind = SeeEditEventsForm(event)
                self.windows.append(wind)
                wind.show()
        except EventNotFound:
            day = self.cal.selectedDate().toString(QtCore.Qt.ISODate).split("-")
            MyNotifications(f"{cnts.NOEVENTDATE} {day[2]}/{day[1]}/{day[0]}")
        
    def AddEvent(self):
        wind = AddEventsForm(self.cal.selectedDate().toString(QtCore.Qt.ISODate))
        self.windows.append(wind)
        wind.show()
    
    def Undo(self):
        try:
            event = bkend.revert()
            MyNotifications(f"{cnts.DISPLAYREMOVEDEVENT} {event.getDate()} {event.getHour()}")
        except NoEventsAdded:
            MyNotifications(cnts.NOEVENT)

class MyNotifications(QtWidgets.QWidget):
    def __init__(self, message, icon=QtWidgets.QMessageBox.Warning, title=cnts.ERRORMESSAGESTITLE, button=QtWidgets.QMessageBox.Discard):
        super().__init__() 
        self.window = QtWidgets.QMessageBox(icon, title, message, button)
        self.window.exec()

class Start(QtWidgets.QWidget):
    def __init__(self, event):
        super().__init__()
        self.setWindowTitle(cnts.NEXTEVENT)
        self.ev = event
        self.window = QtWidgets.QMainWindow()
        self.layout = QtWidgets.QVBoxLayout()
        self.formLayout = QtWidgets.QFormLayout()
        self.horizontalGroupBox = QtWidgets.QGroupBox(self.ev.getDate())
        self.showFunctions = [QtWidgets.QDateTimeEdit(readOnly=True), \
                                                QtWidgets.QTextEdit(readOnly=True), QtWidgets.QTextEdit(readOnly=True), \
                                                QtWidgets.QTextEdit(readOnly=True), QtWidgets.QTextEdit(readOnly=True), \
                                                QtWidgets.QCheckBox()]
          

        manEvents.showEvent(self.formLayout, self.showFunctions, self.ev)

        self.horizontalGroupBox.setLayout(self.formLayout)
        self.layout.addWidget(self.horizontalGroupBox)
        self.setLayout(self.formLayout)
            
if __name__ == "__main__":
    manEvents = ManageEvents()
    app = QtWidgets.QApplication([])
    trayIcon = QtWidgets.QSystemTrayIcon(QtGui.QIcon("icons/calendar.png"), parent=app)
    trayIcon.setToolTip("salve antes de fechar")

    window = []
    for i in range(0, cnts.NUMBEROFDAYSTOSHOW):
        date = bkend.advanceTime(i)
        if date[1] < 10:
            date[1] = f"0{date[1]}"
        if date[2] < 10:
            date[2] = f"0{date[2]}"
        try:
            for event in bkend.getEventsByDate(f"{date[0]}-{date[1]}-{date[2]}"):
                wind = Start(event)
                window.append(wind)
                wind.show()
        except EventNotFound:
            continue

    widget = MyWidget()
    widget.setWindowIcon(QtGui.QIcon('icons/calendar.jpg'))
    widget.resize(200, 800)
    widget.show()
    trayIcon.show()

    sys.exit(app.exec())