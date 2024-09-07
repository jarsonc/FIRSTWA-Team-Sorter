from operator import itemgetter
from typing import OrderedDict
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
    preference = {}
    for team in teamsWithEventDistances:
        sortedEventList = OrderedDict(sorted(teamsWithEventDistances.get(team).items(), key=lambda item: item[1]))
        event, nthChoiceEvent = findEvent(sortedEventList, eventsWithTeamList, team, teamsWithEventDistances, eventsAvailable, preference, 1)
        addPreferenceMetric(nthChoiceEvent, team, teamsWithEventDistances.get(team).get(event), teamsWithEventDistances.get(team))
    return eventsWithTeamList

def findEvent(sortedEventList, eventsWithTeamList, team, teamsWithEventDistances, eventsAvailable, preference, nthChoiceEvent):
    for event in sortedEventList:
        if event not in eventsWithTeamList:
            print("Assigning: ", "{:<5}".format(team), " to new event", event , "at distance", "{:.2f}".format(teamsWithEventDistances.get(team).get(event)))
            eventsWithTeamList[event] = [(team, teamsWithEventDistances.get(team).get(event))]
            preference[team] = nthChoiceEvent
            break
        elif len(eventsWithTeamList[event]) < eventsAvailable.get(event).get(CUSTOM_CAPACITY_TYPE):
            print("Assigning: ", "{:<5}".format(team), " to existing event", event , "at distance", "{:.2f}".format(teamsWithEventDistances.get(team).get(event)))
            eventsWithTeamList.get(event).append((team, teamsWithEventDistances.get(team).get(event)))
            eventsWithTeamList[event] = sorted(eventsWithTeamList.get(event),key=itemgetter(1))
            preference[team] = nthChoiceEvent
            break
        else:
            currentTeamDistance = teamsWithEventDistances.get(team).get(event)
            assignedTeams = sorted(eventsWithTeamList.get(event),key=itemgetter(1))
            for assignedTeam, assignedTeamDistance in assignedTeams:
                currentTeamPreference = list(sortedEventList.keys()).index(event)
                assignedTeamPreference = preference[assignedTeam]
                # If during the course of sorting, the event is full, we double check that there is no team farther away AND lower preferenced (i.e, if this is our 1st preference, we should get in over a 2nd preferenced team)
                if assignedTeamDistance > currentTeamDistance and currentTeamPreference > assignedTeamPreference:
                    eventsWithTeamList.get(event).remove((assignedTeam, assignedTeamDistance))
                    preference.pop(assignedTeam)
                    print("Reallocating: ", "{:<5}".format(team), " to ", event , "at distance", "{:.2f}".format(teamsWithEventDistances.get(team).get(event)))
                    eventsWithTeamList.get(event).append((team, currentTeamDistance))
                    preference[team] = currentTeamPreference
                    print("Rerunning sort for removed team: ", assignedTeam)
                    if team == 63188 or assignedTeam == 63188:
                        emptyPrompt()
                    event, nthChoiceEvent = findEvent(sortedEventList, eventsWithTeamList, assignedTeam, teamsWithEventDistances, eventsAvailable, preference, 1)
                    return event, nthChoiceEvent
            nthChoiceEvent += 1
    return event, nthChoiceEvent

def addPreferenceMetric(nthChoiceEvent, team, distance, allEventDistances):
    if nthChoiceEvent == 1:
        METRIC_DATA[FIRST_CHOICE_EVENT_TEAMS].append(team)
    elif nthChoiceEvent == 2:
        METRIC_DATA[SECOND_CHOICE_EVENT_TEAMS].append(team)
    elif nthChoiceEvent >= 3 and distance > DISTANCE_TO_FLAG:
        print("Flagging team: ", team, "with distance: ", distance, " which is their nth choice: ", nthChoiceEvent)
        print(allEventDistances)
        emptyPrompt()
        METRIC_DATA[FLAGGED_TEAMS].append((team, distance))
    else:
        METRIC_DATA[WEIRD_TEAMS].append(team)

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


