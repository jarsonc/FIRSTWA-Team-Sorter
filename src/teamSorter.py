import json
import os
import pgeocode
from pathlib import Path
import pandas as pd
import urllib.request

from constants import *

def getNumTeams():
    # NOTE: This currently pulls 2024 data, as 2025 data does not yet exist. Verify data source
    r = urllib.request.urlopen(FIRST_WA_TEAMS_URL.format(numTeams = 1) + FIRST_WA_TEAMS_POSTFIX)
    numTeams = json.loads(r.read().decode('utf-8')).get("hits").get("total").get("value")
    return numTeams

def getNumEvents():
    # NOTE: This currently pulls 2024 data, as 2025 data does not yet exist. Verify data source
    r = urllib.request.urlopen(FIRST_WA_EVENTS_URL.format(numEvents = 1) + FIRST_WA_EVENTS_POSTFIX)
    numEvents = json.loads(r.read().decode('utf-8')).get("hits").get("total").get("value")
    return numEvents

def importTeams():
    print("Fetching team data from FIRST API")
    r = urllib.request.urlopen(FIRST_WA_TEAMS_URL.format(numTeams = getNumTeams()) + FIRST_WA_TEAMS_POSTFIX)
    completeTeamData = json.loads(r.read().decode('utf-8')).get("hits").get("hits")
    teamsToSort = {}
    for team in completeTeamData:
        teamData = team.get("_source")
        teamsToSort[teamData.get("team_number_yearly")] = teamData
    return teamsToSort

def importEvents():
    print("Fetching event data from FIRST API")
    r = urllib.request.urlopen(FIRST_WA_EVENTS_URL.format(numEvents = getNumEvents()) + FIRST_WA_EVENTS_POSTFIX)
    completeEventData = json.loads(r.read().decode('utf-8')).get("hits").get("hits")
    eventsToSort = {}
    for event in completeEventData:
        eventData = event.get("_source")
        eventName = eventData.get("event_name")
        if (eventData.get("event_subtype") == QUALIFYING_EVENT_SUBTYPE):
            if CUSTOM_CAPACITY_TYPE not in event.keys():
                eventData["event_capacity"] = DEFAULT_CAPACITY
            for dateName in WEEKEND_DAYS:
                eventName = eventName.replace(dateName, '')
            if eventName in eventsToSort:
                eventsToSort[eventName]["event_capacity"] += eventData["event_capacity"]
            else:
                eventData["event_name"] = eventName
                eventsToSort[eventName] = eventData
    return eventsToSort

def findDistance(team, eventsAvailable):
    distanceUtility = pgeocode.GeoDistance('us')
    teamPostalCode = team.get("team_postalcode")
    eventsAndDistances = {}
    for event in eventsAvailable:
        eventPostalCode = eventsAvailable.get(event).get("event_postalcode")
        eventsAndDistances[event] = distanceUtility.query_postal_code(teamPostalCode, eventPostalCode)
    return eventsAndDistances

def parseTeams(eventsAvailable):
    teamsToSort = importTeams()
    print("Assigning ", len(teamsToSort), " to ", len(eventsAvailable), " events with ", len(eventsAvailable) * DEFAULT_CAPACITY, " spots")
    teamsWithEventDistances = {}
    number = 1
    for team in teamsToSort:
        teamsWithEventDistances[team] = dict(sorted(findDistance(teamsToSort.get(team), eventsAvailable).items(), key=lambda item: item[1]))
        print("Team: ",  "{:<5}".format(team), " | ", number, " out of: ", len(teamsToSort.keys()))
        number += 1
    convertDictToFile(teamsWithEventDistances, TEAMS_WITH_DISTANCES_FILE)
    return teamsWithEventDistances

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

def convertDictToFile(inputDict, path):
    if not os.path.exists(GENERATED_FILE_PATH_ROOT):
        os.makedirs(GENERATED_FILE_PATH_ROOT)
    df = pd.DataFrame.from_dict(inputDict, orient='index')
    df.to_csv(GENERATED_FILE_PATH_ROOT+path)

    
def main():
    eventsAvailable = importEvents()
    teamsWithEventDistances = parseTeams(eventsAvailable)
    eventsWithTeamList = sortTeams(teamsWithEventDistances, eventsAvailable)
    convertDictToFile(eventsWithTeamList, GENERATED_LIST_FILE)
main()