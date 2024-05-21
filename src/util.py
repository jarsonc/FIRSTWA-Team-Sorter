from constants import *

import os
import pandas as pd
import pgeocode

def convertDictToFile(inputDict, desiredFileName, programSelection):
    filePath = GENERATED_FILE_PATH_ROOT + programSelection + "/"
    if not os.path.exists(filePath):
        os.makedirs(filePath)
    df = pd.DataFrame.from_dict(inputDict, orient='index')
    df.to_csv(filePath+desiredFileName)

def checkAlreadySorted(programSelection):
    eventFilePath = GENERATED_FILE_PATH_ROOT + programSelection + "/" + GENERATED_EVENT_FILE
    teamFilePath = GENERATED_FILE_PATH_ROOT + programSelection + "/" + GENERATED_TEAMS_WITH_DISTANCES_FILE
    if os.path.exists(eventFilePath) and os.path.exists(teamFilePath):
        return True
    return False

def importExistingEventsFile(programSelection):
    filePath = GENERATED_FILE_PATH_ROOT + programSelection + "/" + GENERATED_EVENT_FILE
    df = pd.read_csv(filePath, index_col=0)
    existingSort = df.to_dict('index')
    return existingSort

def importExistingTeamsFile(programSelection):
    filePath = GENERATED_FILE_PATH_ROOT + programSelection + "/" + GENERATED_TEAMS_WITH_DISTANCES_FILE
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

def sortTeams(teamsWithEventDistances, eventsAvailable):
    eventsWithTeamList = {}
    closeness = {}
    furthestDistance = ()
    for team in teamsWithEventDistances:
        isClosestEvent = True
        for event in teamsWithEventDistances.get(team):
            if event not in eventsWithTeamList:
                eventsWithTeamList[event] = [team]
                print("Assigning: ", "{:<5}".format(team), " to ", event , "at distance", "{:.2f}".format(teamsWithEventDistances.get(team).get(event)))
                break
            elif len(eventsWithTeamList[event]) < eventsAvailable.get(event).get(CUSTOM_CAPACITY_TYPE):
                eventsWithTeamList.get(event).append(team)
                print("Assigning: ", "{:<5}".format(team), " to ", event , "at distance", "{:.2f}".format(teamsWithEventDistances.get(team).get(event)))
                break
            else:
                print("Failed to assign: ", "{:<5}".format(team), " to full event: ", event)
                isClosestEvent = False
        if not isClosestEvent:
            nthClosestEvent = list(teamsWithEventDistances.get(team).keys()).index(event) + 1
            closeness[team] = nthClosestEvent
        else:
            closeness[team] = 1
        if not bool(furthestDistance):
            furthestDistance = (team, teamsWithEventDistances.get(team).get(event), event)
        elif furthestDistance[1] < teamsWithEventDistances.get(team).get(event):
            furthestDistance = (team, teamsWithEventDistances.get(team).get(event), event)
    print("Furthest assigned team is: ", furthestDistance[0], " with distance: ", furthestDistance[1], "and event: ", furthestDistance[2])
    return eventsWithTeamList


