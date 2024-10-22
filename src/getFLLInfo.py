import re
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

def importFLLTeams(programSelection):
    print("Fetching team data from FIRST API")
    r = urllib.request.urlopen(FIRST_WA_TEAMS_URL.format(numTeams = getNumTeams()) + FIRST_WA_TEAMS_POSTFIX)
    completeTeamData = json.loads(r.read().decode('utf-8')).get("hits").get("hits")
    teamsToSort = {}
    for team in completeTeamData:
        teamData = team.get("_source")
        teamsToSort[teamData.get("team_number_yearly")] = teamData
    convertDictToFile(teamsToSort, GENERATED_TEAMS_FROM_WEBSITE_FILE, programSelection)
    return teamsToSort

def importFLLEvents(programSelection):
    print("Fetching event data from FIRST API")
    r = urllib.request.urlopen(FIRST_WA_EVENTS_URL.format(numEvents = getNumEvents()) + FIRST_WA_EVENTS_POSTFIX)
    completeEventData = json.loads(r.read().decode('utf-8')).get("hits").get("hits")
    eventsToSort = {}
    for event in completeEventData:
        eventData = event.get("_source")
        eventName = re.sub(r'\d+', '', eventData.get("event_name").strip())
        if (eventData.get("event_subtype") == QUALIFYING_EVENT_SUBTYPE):
            if CUSTOM_CAPACITY_TYPE not in event.keys():
                eventData["event_capacity"] = promptForCapacity(eventName)
            for dateName in WEEKEND_DAYS:
                eventName = eventName.replace(dateName, '')
            if eventName in eventsToSort:
                eventsToSort[eventName]["event_capacity"] += eventData["event_capacity"]
            else:
                eventData["event_name"] = eventName
                eventsToSort[eventName] = eventData
    convertDictToFile(eventsToSort, GENERATED_EVENT_FILE, programSelection)
    return eventsToSort

def parseFLLTeams(teamsToSort, eventsAvailable, programSelection, websiteInput):
    totalSpots = 0
    for event in eventsAvailable:
        totalSpots += eventsAvailable.get(event).get(CUSTOM_CAPACITY_TYPE)
    print("Assigning ", len(teamsToSort), " teams to ", len(eventsAvailable), " events (with multi day events combined) with ", totalSpots, " spots")
    if len(teamsToSort) > totalSpots:
        raise Exception("Not enough event spots for teams")
    teamsWithEventDistances = {}
    number = 1
    for team in teamsToSort:
        teamsWithEventDistances[team] = dict(sorted(findDistanceByPostalCode(teamsToSort.get(team), eventsAvailable, websiteInput).items(), key=lambda item: item[1]))
        print("Team: ",  "{:<5}".format(team), " | ", number, " out of: ", len(teamsToSort.keys()))
        number += 1
    convertDictToFile(teamsWithEventDistances, GENERATED_WEBSITE_TEAMS_WITH_ALL_EVENT_DISTANCES if websiteInput else GENERATED_MANUAL_TEAMS_WITH_ALL_EVENT_DISTANCES, programSelection)
    print("Finished sorting and saving")
    return teamsWithEventDistances
