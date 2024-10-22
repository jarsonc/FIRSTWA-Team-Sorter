import math
from operator import itemgetter
from constants import *

import os
import pandas as pd
import pgeocode

from metrics import *

HAS_REGISTERED_ADDED_FIELD = "Registered With FIRSTWA"

def convertDictToFile(inputDict, desiredFileName, programSelection):
    filePath = GENERATED_FILE_PATH_ROOT + programSelection + "/"
    if not os.path.exists(filePath):
        os.makedirs(filePath)
    df = pd.DataFrame.from_dict(inputDict, orient='index')
    df.to_csv(filePath+desiredFileName)

def checkDataExists(programSelection):
    eventFilePath = GENERATED_FILE_PATH_ROOT + programSelection + "/" + GENERATED_EVENT_FILE
    if os.path.exists(eventFilePath):
        return True
    return False

def checkAlreadySorted(programSelection):
    sortFilePath = GENERATED_FILE_PATH_ROOT + programSelection + "/" + GENERATED_LIST_FILE
    if os.path.exists(sortFilePath):
        return True
    return False

def importExistingSort(programSelection):
    filePath = GENERATED_FILE_PATH_ROOT + programSelection + "/" + GENERATED_LIST_FILE
    df = pd.read_csv(filePath, index_col=0)
    existingSort = df.to_dict('index')
    return existingSort


def importExistingEventsFile(programSelection):
    filePath = GENERATED_FILE_PATH_ROOT + programSelection + "/" + GENERATED_EVENT_FILE
    df = pd.read_csv(filePath, index_col=0)
    existingSort = df.to_dict('index')
    for event in existingSort:
        capacity = existingSort.get(event).get(CUSTOM_CAPACITY_TYPE)
        if math.isnan(capacity):
            existingSort[event][CUSTOM_CAPACITY_TYPE] = promptForCapacity(event)
    return existingSort

def importExistingWebsiteTeamsFile(programSelection):
    filePath = GENERATED_FILE_PATH_ROOT + programSelection + "/" + GENERATED_TEAMS_FROM_WEBSITE_FILE
    df = pd.read_csv(filePath, index_col=0)
    print(df)
    existingSort = df.to_dict('index')
    return existingSort

def importExistingManualTeamsFile(programSelection):
    filePath = GENERATED_FILE_PATH_ROOT + programSelection + "/" + GENERATED_TEAMS_FROM_MANUAL_FILE
    df = pd.read_csv(filePath, index_col=0)
    existingSort = df.to_dict('index')
    return existingSort


def importExistingWebsiteTeamsWithAllEventDistancesFile(programSelection):
    filePath = GENERATED_FILE_PATH_ROOT + programSelection + "/" + GENERATED_WEBSITE_TEAMS_WITH_ALL_EVENT_DISTANCES
    df = pd.read_csv(filePath, index_col=0)
    existingSort = df.to_dict('index')
    return existingSort

def importExistingManualTeamsWithAllEventDistancesFile(programSelection):
    filePath = GENERATED_FILE_PATH_ROOT + programSelection + "/" + GENERATED_MANUAL_TEAMS_WITH_ALL_EVENT_DISTANCES
    df = pd.read_csv(filePath, index_col=0)
    existingSort = df.to_dict('index')
    return existingSort


def findDistanceByPostalCode(team, eventsAvailable, websiteInput):
    distanceUtility = pgeocode.GeoDistance('us')
    teamPostalCode = team.get(TEAM_POSTAL_CODE_DATATYPE if websiteInput else TEAM_POSTAL_CODE_DATATYPE_MANUAL_INPUT)
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

def promptForCapacity(eventName):
    """
    inputPrompt = "No capacity found for event: " + eventName + "\nEnter capacity desired: "
    while True:
        try:
            capcity = int(input(inputPrompt))
        except ValueError:
            print("Invalid capacity entered. Please enter a whole number.")
            continue
        else:
            break
    return capcity
    """
    return 25

def emptyPrompt():
    input("Press Enter to continue...")

def promptForInputSource():
    inputPrompt = "Would you like to use FIRST's API data, or upload a file? Enter 'y' for API data, anything else for upload."
    return "y" in input(inputPrompt).lower()

def getTeamsFromInput(programSelection):
    # This logic currently adds a column labeled "HAS_REGISTERED_ADDED_FIELD", which marks if they've paid
    # We want to eventually add preference logic. For initial run, we'll just sort paid teams
    #
    # filePath = validateFilePath()
    # allTeams = pd.read_excel(filePath, sheet_name=0)
    # allTeams.set_index('Team Number', drop=False, inplace=True)
    # allTeams[HAS_REGISTERED_ADDED_FIELD]=0
    # registeredTeams = pd.read_excel(filePath, sheet_name=1, header=None).iloc[:, 0]
    # for team in registeredTeams:
    #     allTeams.loc[allTeams['Team Number'] == team, HAS_REGISTERED_ADDED_FIELD] = 1
    # convertedDict = allTeams.to_dict('index')
    # convertDictToFile(convertedDict, GENERATED_TEAMS_FROM_MANUAL_FILE, programSelection)
    # return convertedDict
    filePath = validateFilePath()
    allTeams = pd.read_excel(filePath, sheet_name=0)
    allTeams.set_index('Team Number', drop=False, inplace=True)
    allTeams[HAS_REGISTERED_ADDED_FIELD]=0
    registeredTeams = pd.read_excel(filePath, sheet_name=1, header=None).iloc[:, 0]
    teamsToSort = {}
    for team in registeredTeams:
        teamsToSort.update(allTeams.loc[allTeams['Team Number'] == team].to_dict('index'))
    convertDictToFile(teamsToSort, GENERATED_TEAMS_FROM_MANUAL_FILE, programSelection)
    return teamsToSort


def validateFilePath():
    """
    inputPrompt = "Enter existing file path: "
    while True:
        try:
            filePath = input(inputPrompt)
            print("Entered: ", filePath)
            if os.path.isfile(filePath):
                return filePath
            else:
                print("Invalid path entered. Try again")
                continue
        except:
            break
    """
    return "/Users/jasoncheng/Desktop/FLL_Team_Sorter/src/List for Jason.xlsx"
    