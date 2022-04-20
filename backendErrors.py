class EventNotFound(Exception):
    '''
        Common implementation is to insert the error causing date in the constructor
    '''
    pass

class DataInitError(Exception):
    '''
        Error occuring when loading the file
    '''
    pass

class DateTimeError(Exception):
    '''
        error with a date or time given
    '''
    pass

class EventAlreadyExists(Exception):
    '''
        error thrown when a event already exists
    '''
    pass

class NoEventsAdded(Exception):
    '''
        represents the inexistance of events added since the start 
    '''
    pass

class EventNotFound(Exception):
    '''
        Represents the inexistance of a event
    '''
    pass

class SavingError(Exception):
    '''
        Error printed when there was an error saving
    '''
    pass