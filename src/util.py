from operator import itemgetter
from constants import *

import os
import pandas as pd
import pgeocode

from metrics import *

def convertDictToFile(inputDict, desiredFileName, programSelection):
    filePath = GENERATED_FILE_PATH_ROOT + programSelection + "/"
    if not os.path.exists(filePath):
        os.makedirs(filePath)
    df = pd.DataFrame.from_dict(inputDict, orient='index')
    df.to_csv(filePath+desiredFileName)

def checkDataExists(programSelection):
    eventFilePath = GENERATED_FILE_PATH_ROOT + programSelection + "/" + GENERATED_EVENT_FILE
    teamFilePath = GENERATED_FILE_PATH_ROOT + programSelection + "/" + GENERATED_TEAMS_WITH_ALL_EVENT_DISTANCES
    if os.path.exists(eventFilePath) and os.path.exists(teamFilePath):
        return True
    return False

def checkAlreadySorted(programSelection):
    sortFilePath = GENERATED_FILE_PATH_ROOT + programSelection + "/" + GENERATED_LIST_FILE
    if os.path.exists(sortFilePath):
        return True
    return False


def importExistingEventsFile(programSelection):
    filePath = GENERATED_FILE_PATH_ROOT + programSelection + "/" + GENERATED_EVENT_FILE
    df = pd.read_csv(filePath, index_col=0)
    existingSort = df.to_dict('index')
    return existingSort

def importExistingTeamsFile(programSelection):
    filePath = GENERATED_FILE_PATH_ROOT + programSelection + "/" + GENERATED_TEAMS_FILE
    df = pd.read_csv(filePath, index_col=0)
    existingSort = df.to_dict('index')
    return existingSort

def importExistingTeamsWithAllEventDistancesFile(programSelection):
    filePath = GENERATED_FILE_PATH_ROOT + programSelection + "/" + GENERATED_TEAMS_WITH_ALL_EVENT_DISTANCES
    df = pd.read_csv(filePath, index_col=0)
    existingSort = df.to_dict('index')
    return existingSort

def findDistanceByPostalCode(team, eventsAvailable):
    distanceUtility = pgeocode.GeoDistance('us')
    teamPostalCode = team.get(TEAM_POSTAL_CODE_DATATYPE)
    eventsAndDistances = {}
    for event in eventsAvailable:
        eventPostalCode = eventsAvailable.get(event).get(EVENT_POSTAL_CODE_DATATYPE)
        eventsAndDistances[event] = distanceUtility.query_postal_code(teamPostalCode, eventPostalCode)
    return eventsAndDistances

def findPostalCodeByCity(importedData):
    distanceUtility = pgeocode.Nominatim('us')
    # Pulls first 5 cities with name from event in USA
    postalCodeGuess = distanceUtility.query_location(importedData["city"], top_k=100)
    if postalCodeGuess.empty:
        return manuallyPromptForPostalCode(importedData)
    else:
        # Picks the first city in the state we're looking in, then converts to postal code (type str)
        filteredPostalCode = postalCodeGuess[postalCodeGuess['state_code'] == STATE_ARG]
        if not filteredPostalCode.size:
            return manuallyPromptForPostalCode(importedData)
        return filteredPostalCode["postal_code"].iloc[0]

def manuallyPromptForPostalCode(importedData):
    inputPrompt = "Post code for: {} not found. \nTeam data: {} \nManually enter a 5 digit zip here: ".format(importedData["city"], importedData)
    inputPostalCode = input(inputPrompt)
    return inputPostalCode

def plotTeamsAgainstEvents(postalcode):
    nomi = pgeocode.Nominatim('us')
    postal_code = postalcode
    location = nomi.query_postal_code(postalcode)
    print(location.latitude, location.longitude)
    emptyPrompt()

def createEventKeysWithTeams(eventsAvailable, teamsWithEventDistances):
    eventsWithSortedTeams = {}
    for event in eventsAvailable:
        orderedTeams = {}
        for team in teamsWithEventDistances:
            orderedTeams[team] = teamsWithEventDistances.get(team).get(event)
        eventsWithSortedTeams[event] = dict(sorted(orderedTeams.items(), key=lambda item: item[1]))
    return eventsWithSortedTeams

def promptForRerun():
    inputPrompt = "Existing team/event list found. Use existing data? (Y/N)"
    return "y" in input(inputPrompt).lower()

def promptForReSort():
    inputPrompt = "Existing sort found. Re-allocate events? (Y/N) \n NOTE: This will override any existing sorts unless the file is backed up)"
    return "y" in input(inputPrompt).lower()

def emptyPrompt():
    input("Press Enter to continue...")