from datetime import datetime, timedelta
import backend.backendConstants as bckendC
import backend.backendErrors as Errors
import platform
import random
import json
import os

class Event:
    def __init__(self, date=None, time=None, place=None, procN=None, trib=None, name=None, id=None, dict=None, test=False):
        if not test:    
            if dict == None:    
                self.struct = {
                    bckendC.LABELDATE: date, 
                    bckendC.LABELHOUR: time,
                    bckendC.LABELPLACE: place, 
                    bckendC.LABELMATTER: procN, 
                    bckendC.LABELSUPPERIOR: trib, 
                    bckendC.LABELNAME: name,
                    bckendC.LABELSTATUS: False,
                    bckendC.LABELID: id
                }
                #adicionar prevenção de erro
                with open(os.path.join(bckendC.PATHFILEDIR, bckendC.PATHFILE), "a") as conf: 
                    conf.write(json.dumps(self.struct) + "\n")           
            else:
                self.struct = dict
        else:
            self.struct = {
                bckendC.LABELDATE: date, 
                bckendC.LABELHOUR: time,
                bckendC.LABELPLACE: place, 
                bckendC.LABELMATTER: procN, 
                bckendC.LABELSUPPERIOR: trib, 
                bckendC.LABELNAME: name,
                bckendC.LABELSTATUS: False,
                bckendC.LABELID: id
            }
    
    #check errors
    #def __eq__(self, other):
    #    if not isinstance(self, Event) or not isinstance(other, Event):
    #        print("types not accepted")
    #    else:
    #        return self.getDate() == other.getDate() and self.getEventHour() == other.getEventHour()

    #Setters

    def setDate(self, date) -> None:
        self.struct[bckendC.LABELDATE] = date

    def setHour(self, hour) -> None:
        self.struct[bckendC.LABELHOUR] = hour

    def setPlace(self, place) -> None:
        self.struct[bckendC.LABELPLACE] = place

    def setMatter(self, matter) -> None:
        self.struct[bckendC.LABELMATTER] = matter

    def setSupperior(self, supperior) -> None:
        self.struct[bckendC.LABELSUPPERIOR] = supperior

    def setName(self, name) -> None:
        self.struct[bckendC.LABELNAME] = name

    def setStatus(self, status) -> None:
        if isinstance(status, bool):
            self.struct[bckendC.LABELSTATUS] = status

    #Getters

    def getDate(self) -> str:
        return self.struct[bckendC.LABELDATE]

    def getHour(self) -> str:
        return self.struct[bckendC.LABELHOUR]

    def getPlace(self) -> str:
        return self.struct[bckendC.LABELPLACE]

    def getMatter(self) -> str:
        return self.struct[bckendC.LABELMATTER]

    def getSupperior(self) -> str:
        return self.struct[bckendC.LABELSUPPERIOR]

    def getName(self) -> str:
        return self.struct[bckendC.LABELNAME]

    def getStatus(self) -> bool:
        return self.struct[bckendC.LABELSTATUS]

    def getEvent(self) -> dict:
        return self.struct

    def getId(self) -> int:
        return self.struct[bckendC.LABELID]

    def isEqual(self, id) -> bool:
        return self.getId() == id

    def exists(self, date, hour) -> bool:
        return self.getDate() == date and self.getHour() == hour

class Backend:
    def __init__(self):
        self.ids = {bckendC.LABELID: []}
        self.events = {}
        self.addedEvents = []
        self.saved = False
        self.configFile()
        self.parseFile()

    #just made for linux and windows
    def configFile(self):
        '''
            configures the bakcend config file correctly when the os in 
            considered
        '''
        platfm = platform.platform()
        if platfm.split("-")[0] not in bckendC.PLATFORM:
            if 'Linux' not in bckendC.PLATFORM:
                self.changeConfFile("\\", "/", platfm)
            else:
                self.changeConfFile("/", "\\", platfm)

    def changeConfFile(self, oldDiv, div, plat):
        '''
            Auxiliar function for correction the configuration file
        '''
        with open("backendConstants.py", 'r') as file:
            lines = file.readlines()
        with open("backendConstants.py", 'w') as const:
            for line in lines:
                if "PATH" in line:
                    line = line.split("=")
                    line[1] = line[1].replace(oldDiv, div)
                    const.write(f"{line[0]}={line[1]}")
                elif "PLATFORM" in line:
                    const.write(f"PLATFORM = \"{plat}\"\n")
                else:
                    const.write(line)

    def parseFile(self):
        #path to the curent project dir
        dirPath = bckendC.PATHFILEDIR.split(bckendC.PATHDIRDIV)
        if dirPath[-1] not in os.listdir(bckendC.PATHDIRDIV.join(dirPath[:-1]) + bckendC.PATHDIRDIV):
            os.mkdir(bckendC.PATHFILEDIR)
        
        if bckendC.PATHFILE not in os.listdir(bckendC.PATHFILEDIR):
            with open(os.path.join(bckendC.PATHFILEDIR, bckendC.PATHFILE), "w") as conf:
                conf.write(f"{bckendC.COMMENTCARACTER} {datetime.now()}\n")

        else:
            with open(os.path.join(bckendC.PATHFILEDIR, bckendC.PATHFILE), "r") as conf:
                lines = conf.readlines()
            for line in lines:
                if bckendC.COMMENTCARACTER not in line:
                    if bckendC.STARTIDS in line:
                        self.ids = json.loads(line[1:])
                    else:
                        event = Event(dict=json.loads(line))
                        if event.getDate() not in self.events.keys():
                            self.events[event.getDate()] = [event]
                        else:
                            self.events[event.getDate()].append(event)
                            self.ids[bckendC.LABELID].append(event.getId())

    def isDate(self, check):
        if not isinstance(check, str):
            return False
        if "-" not in check:
            return False
        if check.count("-") != 2:
            return False
        for value in check.split("-"):
            if not value.isdigit():
                return False
        return True

    def isTime(self, check):
        if not isinstance(check, str):
            return False
        if ":" not in check:
            return False
        if check.count(":") != 1:
            return False
        for value in check.split(":"):
            if not value.isdigit():
                return False
        return True

    def revert(self) -> Event:
        '''
            Removes the last event inserted in the system and returns it
            Raises NoEventsAdded error
        '''
        if len(self.addedEvents) == 0:
            raise Errors.NoEventsAdded
        else:
            evn = self.addedEvents.pop()
            self.events[evn.getDate()].remove(evn)
            self.ids[bckendC.LABELID].remove(evn.getId())
            return evn

    def removeEvent(self, event) -> Event:
        '''
            Removes a event inserted in the system and returns it
            Raises EventNotFound
        '''
        for ev in self.addedEvents:
            if ev.isEqual(event.getId()):
                self.addedEvents.remove(event)
        if event.getDate() not in self.events.keys() or event.getId() not in self.ids[bckendC.LABELID]:
            raise Errors.EventNotFound
        elif event not in self.events[event.getDate()]:
            raise Errors.EventNotFound
        else:
            self.ids[bckendC.LABELID].remove(event.getId())
            self.events[event.getDate()].remove(event)
            return event 

    def save(self) -> None:
        dirPath = bckendC.PATHFILEDIR.split(bckendC.PATHDIRDIV)
        if dirPath[-1] not in os.listdir(bckendC.PATHDIRDIV.join(dirPath[:-1]) + bckendC.PATHDIRDIV):
            os.mkdir(bckendC.PATHFILEDIR)
        
        if bckendC.PATHFILE2 not in os.listdir(bckendC.PATHFILEDIR):
            with open(os.path.join(bckendC.PATHFILEDIR, bckendC.PATHFILE2), "w") as conf:
                conf.write(f"{bckendC.COMMENTCARACTER} {datetime.now()}\n")

        #try:
        with open(os.path.join(bckendC.PATHFILEDIR, bckendC.PATHFILE), "r") as oldconf:
            lines = oldconf.readlines()
        with open(os.path.join(bckendC.PATHFILEDIR, bckendC.PATHFILE2), "w") as conf: 
            conf.write(f"{bckendC.COMMENTCARACTER} {datetime.now()}\n")

            for key in self.events.keys():
                for event in self.events[key]:
                    if event.getStatus() ==  False:
                        conf.write(f"{json.dumps(event.getEvent())}\n")
            for line in lines:
                if bckendC.COMMENTCARACTER not in line:
                    continue
                else:
                    conf.write(line)
            conf.write(f"{bckendC.STARTIDS}{json.dumps(self.getIds())}\n")
            for key in self.events.keys():
                for event in self.events[key]:
                    if event.getStatus() ==  True:
                        conf.write(f"{bckendC.COMMENTCARACTER}{json.dumps(event.getEvent())}\n")
            
        if not self.saved:
            self.saved = True
            with open("backendConstants.py", "r") as bC:
                lines = bC.readlines()
            with open("backendConstants.py", "w") as bC:
                for line in lines:
                    if "=" in line:
                        line = line.split(" = ")
                        if "PATHFILE" == line[0]:
                            aux = line[1]
                        elif "PATHFILE2" == line[0]:
                            bC.write(f"PATHFILE = {line[1]}")
                            bC.write(f"PATHFILE2 = {aux}")
                        else:
                            bC.write(f"{line[0]} = {line[1]}")
                    else:
                        bC.write(f"{line}")
                  
        #except Exception as e:    
            #raise Errors.SavingError(e)
    
    def changeEvent(self, event, date="", time="", place="", procN="", trib="",name="", status=False, id=None) -> None:
        if not isinstance(event, Event):
            return
        if event.getId() not in self.ids[bckendC.LABELID]:
            raise Errors.EventNotFound
        if self.isDate(date) and self.isTime(time):
            if date not in self.events.keys() and date != event.getDate():
                self.events[date] = [event]
                self.events[event.getDate()].remove(event)
            for ev in self.events[date]:
                if ev.getId() == id:
                    continue
                elif ev.getHour() == time:
                    raise Errors.EventAlreadyExists
            if date != event.getDate():
                self.events[date].append(event)
                self.events[event.getDate()].remove(event)
            event.setDate(date)
            event.setHour(time)
            event.setPlace(place)
            event.setMatter(procN)
            event.setSupperior(trib)
            event.setName(name)
            event.setStatus(status)
        else:
            raise Errors.DataInitError

    #SETTERS
    
    def setStatusEvent(self, date, hour, status):
        if date in self.events.keys():
            done = False
            for event in self.events[date]:
                if hour == event.getHour():
                    event.setStatus(status)
            if not done: return "ProcNum inexistante"    
        else: 
            raise Errors.EventNotFound(f"{date} {hour}")

    def setEvent(self, date=None, time=None, place=None, procN=None, trib=None, name=None) -> None:
        '''
            creates a new event if it doesn't exist
            raises DateTimeError
        '''
        if self.isDate(date) and self.isTime(time):
            if date not in self.events.keys():
                id = self.giveID()
                newEvent = Event(date, time, place, procN, trib, name, id)
                self.events[date] = [newEvent]
                self.addedEvents.append(newEvent)
                self.ids[bckendC.LABELID].append(id)
            else:
                for event in self.events[date]: 
                    if event.exists(date, time):
                        raise Errors.EventAlreadyExists
                id = self.giveID()
                newEvent = Event(date, time, place, procN, trib, name, id=id)
                self.events[date].append(newEvent)
                self.addedEvents.append(newEvent)
                self.ids[bckendC.LABELID].append(id)
        elif not self.isDate(date):
            raise Errors.DateTimeError(f"{date}")
        else:
            raise Errors.DateTimeError(f"{time}")

    #GETTERS

    def getEvents(self) -> dict:
        return self.events

    def getEventsByDate(self, date) -> list:
        '''
            returns a list of all events in a given date
            raises an error if the date given isn't in the rigth format
            raises an error if the given date doesnt exist in our db
        '''
        if not self.isDate(date):
            raise Errors.DataInitError(f"{date}")
        if date not in self.events.keys():
            raise Errors.EventNotFound(date)
        else:
            return self.events[date]  

    def currentTime(self) -> list:
        '''
            returns a list of integers representing yyyy mm dd
        '''
        return [int(i) for i in str(datetime.date(datetime.now())).split("-")]

    def advanceTime(self, Days) -> list:
        ''''
        Returns the current date + Days days
        output = [int(year), int(month), int(day)]   
        '''
        delta = timedelta(days = Days)
        return [int(i) for i in str(datetime.date(datetime.now() + delta)).split("-")]

    def getEvent(self, date, procN) -> Event:
        '''
            returns the requested event
            raises Event not found in case of an error 
        '''
        for event in self.events[date]:
            if event.getProcN() == procN:
                return event
        raise Errors.EventNotFound(date) 

    def getIds(self) -> dict:
        return self.ids

    #Event Handling

    def giveID(self) -> int:
        id = random.randrange(1, bckendC.RANDOMMAX)
        while id in self.ids[bckendC.LABELID]:
            id = random.randrange(1, bckendC.RANDOMMAX)
        return id

    def getEventDate(self, event) -> str:
        return event.getDate()

    def getEventHour(self, event) -> str:
        '''
            returns a string in hh:mm format
        '''
        return event.getHour()

    def getEventPlace(self, event) -> str:
        return event.getPlace()

    def getEventMatter(self, event) -> str:
        return event.getMatter()

    def getEventSupperior(self, event) -> str:
        return event.getSupperior()

    def getEventName(self, event) -> str:
        return event.getName()

    def getEventStatus(self, event) -> bool:
        return event.getStatus()

if __name__ == "__main__":
    back = Backend()
    #back.addEvent("2022-01-09", "12:00", "Casa2", 19758, "Com.lisboa", "europa")
    #print(back.giveID())
    pass