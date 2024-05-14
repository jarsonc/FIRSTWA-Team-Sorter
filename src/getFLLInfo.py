from constants import *
from util import *

import json
import urllib.request

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

def importFLLTeams():
    print("Fetching team data from FIRST API")
    r = urllib.request.urlopen(FIRST_WA_TEAMS_URL.format(numTeams = getNumTeams()) + FIRST_WA_TEAMS_POSTFIX)
    completeTeamData = json.loads(r.read().decode('utf-8')).get("hits").get("hits")
    teamsToSort = {}
    for team in completeTeamData:
        teamData = team.get("_source")
        teamsToSort[teamData.get("team_number_yearly")] = teamData
    return teamsToSort

def importFLLEvents():
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

def parseFLLTeams(eventsAvailable):
    teamsToSort = importFLLTeams()
    print("Assigning ", len(teamsToSort), " to ", len(eventsAvailable), " events with ", len(eventsAvailable) * DEFAULT_CAPACITY, " spots")
    teamsWithEventDistances = {}
    number = 1
    for team in teamsToSort:
        teamsWithEventDistances[team] = dict(sorted(findDistanceByPostalCode(teamsToSort.get(team), eventsAvailable).items(), key=lambda item: item[1]))
        print("Team: ",  "{:<5}".format(team), " | ", number, " out of: ", len(teamsToSort.keys()))
        number += 1
    convertDictToFile(teamsWithEventDistances, TEAMS_WITH_DISTANCES_FILE)
    return teamsWithEventDistances

