import json
import pgeocode
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
    r = urllib.request.urlopen(FIRST_WA_TEAMS_URL.format(numTeams = getNumTeams()) + FIRST_WA_TEAMS_POSTFIX)
    completeTeamData = json.loads(r.read().decode('utf-8')).get("hits").get("hits")
    teamsToSort = {}
    for team in completeTeamData:
        teamData = team.get("_source")
        teamsToSort[teamData.get("team_number_yearly")] = teamData
    return teamsToSort

def importEvents():
    r = urllib.request.urlopen(FIRST_WA_EVENTS_URL.format(numEvents = getNumEvents()) + FIRST_WA_EVENTS_POSTFIX)
    completeEventData = json.loads(r.read().decode('utf-8')).get("hits").get("hits")
    eventsToSort = {}
    for event in completeEventData:
        eventData = event.get("_source")
        if (eventData.get("event_subtype") == QUALIFYING_EVENT_SUBTYPE):
            if CUSTOM_CAPACITY_TYPE not in event.keys():
                eventData["event_capacity"] = DEFAULT_CAPACITY
            eventsToSort[eventData.get("event_name")] = eventData
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
    df = pd.DataFrame.from_dict(teamsWithEventDistances, orient='index')
    df.to_csv(TEAMS_WITH_DISTANCES_FILE)
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

def main():
    eventsAvailable = importEvents()
    teamsWithEventDistances = parseTeams(eventsAvailable)
    eventsWithTeamList = sortTeams(teamsWithEventDistances, eventsAvailable)
    df = pd.DataFrame.from_dict(eventsWithTeamList, orient='index')
    df.to_csv('eventsWithTeamList.csv')

main()