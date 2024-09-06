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
    teamFilePath = GENERATED_FILE_PATH_ROOT + programSelection + "/" + GENERATED_TEAMS_WITH_DISTANCES_FILE
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
        print(teamsWithEventDistances)
        emptyPrompt()
        closenessOfAssignment = 1
        sortedEventList = dict(sorted(teamsWithEventDistances.get(team).items(), key=lambda item: item[1]))
        for event in sortedEventList:
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
                closenessOfAssignment += 1
        closeness[team] = closenessOfAssignment
        if closenessOfAssignment == 1:
            METRIC_DATA[FIRST_CHOICE_EVENT_TEAMS].append(team)
        elif closenessOfAssignment == 2:
            METRIC_DATA[SECOND_CHOICE_EVENT_TEAMS].append(team)
        elif closenessOfAssignment >= 3 and teamsWithEventDistances.get(team).get(event) > DISTANCE_TO_FLAG:
            METRIC_DATA[FLAGGED_TEAMS].append(team)
        else:
            METRIC_DATA[WEIRD_TEAMS].append(team)
        if not bool(furthestDistance):
            furthestDistance = (team, teamsWithEventDistances.get(team).get(event), event)
        elif furthestDistance[1] < teamsWithEventDistances.get(team).get(event):
            furthestDistance = (team, teamsWithEventDistances.get(team).get(event), event)
    print("Furthest assigned team is: ", furthestDistance[0], " with distance: ", furthestDistance[1], "and event: ", furthestDistance[2])
    METRIC_DATA[FURTHEST_DISTANCE_METRIC] =  (furthestDistance[0], furthestDistance[1])
    return eventsWithTeamList

def promptForRerun():
    inputPrompt = "Existing team/event list found. Use existing data? (Y/N)"
    return "y" in input(inputPrompt).lower()

def promptForReSort():
    inputPrompt = "Existing sort found. Re-allocate events? (Y/N) \n NOTE: This will override any existing sorts unless the file is backed up)"
    return "y" in input(inputPrompt).lower()

def emptyPrompt():
    input("Press Enter to continue...")


