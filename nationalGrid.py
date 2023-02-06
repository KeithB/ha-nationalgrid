#!/usr/bin/python3

# General imports
import datetime
import aiohttp
# Local imports
from .const import ( DFS_DATASTORE, DFS_QUERY_PARAMETERS, CACHE_EXPIRY )


## Used to aid sorting
def dfs_start_time(dfs_requirement):
  return dfs_requirement['start']


class NationalGridClient:

  def __init__(self, session: aiohttp.ClientSession):
    self._polling_dfs = False
    self._last_dfs_poll = None
    self._session = session
    self._dfsData = None
 
  ##  
  ## Pulls the current data from NG ESO and then extracts only the records that apply today.
  ##
  async def async_get_todays_dfs_requirements(self, dfsDate=None):

    self._polling_dfs = True
    requirements = list()
    jsonData = None
    queryDFS = False 
    today = datetime.date.today()
    if dfsDate is not None:
      today = dfsDate

    ## Retain an element of control over how often we actually bug NG ESO
    if self._dfsData is None:
      queryDFS = True
    else:
      if self._last_dfs_poll is None:
        queryDFS = True
      else: 
        cacheExpiryTime = (self._last_dfs_poll+datetime.timedelta(minutes=CACHE_EXPIRY))
        queryDFS = ( datetime.datetime.now() > cacheExpiryTime )
    

    if queryDFS:
      if DFS_DATASTORE is not None:
        queryURL = DFS_DATASTORE
        if DFS_QUERY_PARAMETERS is not None:
          queryURL = queryURL+"&"+DFS_QUERY_PARAMETERS
      
        async with self._session.get(queryURL) as response:
          jsonData = await response.json()
  
      if jsonData:
        for record in jsonData['result']['records']:
          requestDate = str(record['Delivery Date'])
          if requestDate == str(today):
            start = datetime.datetime.strptime( requestDate+" "+record['From GMT'], "%Y-%m-%d %H:%M" )
            end = datetime.datetime.strptime( requestDate+" "+record['To GMT'], "%Y-%m-%d %H:%M" )
            dfsRequirement = { 'start': start, 'end': end, 'minutes': ((end - start).total_seconds() // 60) }
            requirements.append( dfsRequirement )
        requirements.sort(key=dfs_start_time)
        self._dfsData = requirements
        
    self._polling_dfs = False
    self._last_dfs_poll = datetime.datetime.now()

##
## Derives current DFS status based on time of day and requirements:
##   Inactive    : No requirements until at least midnight.
##   Scheduled   : DFS requirements scheduled for later in the day.
##   Active      : Currently in a DFS requirement window.
##
  def get_current_dfs_status(self, dfsDate=None) -> str:

    currentStatus = 'Unknown'
    currentTime = datetime.datetime.now()
    if dfsDate is not None:
      currentTime = datetime.datetime.strptime( dfsDate+" "+currentTime.strftime('%H:%M'), "%Y-%m-%d %H:%M" )

    if self._dfsData is not None:
      currentStatus = 'Inactive'
      for thisAsk in self._dfsData:
        if thisAsk['start'] < currentTime < thisAsk['end']:
          currentStatus = 'Active'
          break
        if currentTime < thisAsk['start']:
          currentStatus = 'Scheduled'   
 
    return currentStatus

##
## Gets the start time of the current (DFS active) or next (DFS scheduled) session.
## Returns None if inactive.
##
  def get_dfs_session_start(self, dfsDate=None):

    currentTime = datetime.datetime.now()
    if dfsDate is not None:
      currentTime = datetime.datetime.strptime( dfsDate+" "+currentTime.strftime('%H:%M'), "%Y-%m-%d %H:%M" )
    
    sessionStart = None
    # It's actually easier to do this by working backwards from the identified end of session.
    # Otherwise you have to work out the end of every session from the first record to avoid reporting a shrinking
    # session.
    sessionEnd = self.get_dfs_session_end(dfsDate)

    if self._dfsData is not None:
      dfsData = self._dfsData
      dfsData.sort(reverse=True, key=dfs_start_time)
      for request in dfsData:
        if sessionStart is None:
          if sessionEnd == request['end']:
            sessionStart = request['start']
        else:
          if request['end'] == sessionStart:
            sessionStart = request['start']
          else:
            break
  
    return sessionStart

##
## Gets the end time of the current (DFS active) or next (DFS scheduled) session.
## Returns None if inactive.
##
  def get_dfs_session_end(self, dfsDate=None):

    currentTime = datetime.datetime.now()
    if dfsDate is not None:
      currentTime = datetime.datetime.strptime( dfsDate+" "+currentTime.strftime('%H:%M'), "%Y-%m-%d %H:%M" )  
    sessionEnd = None

    if self._dfsData is not None:
      dfsData = self._dfsData
      dfsData.sort(key=dfs_start_time)
      for request in dfsData:
        if sessionEnd is None:
          if (request['start'] >= currentTime) or (request['start'] < currentTime < request['end']):
            sessionEnd = request['end']
        else:
          if request['start'] == sessionEnd:
            sessionEnd = request['end']
          else:
            break
  
    return sessionEnd

##
## Total time ESO is requesting flexibility today
##
  def get_todays_total_dfs_request(self) -> int:
 
    requestedMinutes = 0

    if self._dfsData is not None:
      for request in self._dfsData:
        requestedMinutes = requestedMinutes + request['minutes']

    return requestedMinutes

##
## Remaining time ESO is requesting flexibility today
##
  def get_todays_outstanding_dfs_request(self) -> int:
  
    outstandingMinutes = 0
    currentTime = datetime.datetime.now()

    if self._dfsData is not None:
      for request in self._dfsData:
        if request['start'] > currentTime:
          outstandingMinutes = outstandingMinutes + request['minutes']
        if request['start'] < currentTime < request['end']:
          outstandingMinutes = outstandingMinutes + ((request['end']-currentTime).total_seconds() // 60)
  
    return outstandingMinutes
