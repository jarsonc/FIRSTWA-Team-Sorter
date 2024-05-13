from constants import *

import os
import pandas as pd
import pgeocode

def convertDictToFile(inputDict, path):
    if not os.path.exists(GENERATED_FILE_PATH_ROOT):
        os.makedirs(GENERATED_FILE_PATH_ROOT)
    df = pd.DataFrame.from_dict(inputDict, orient='index')
    df.to_csv(GENERATED_FILE_PATH_ROOT+path)

def findDistance(team, eventsAvailable):
    distanceUtility = pgeocode.GeoDistance('us')
    teamPostalCode = team.get("team_postalcode")
    eventsAndDistances = {}
    for event in eventsAvailable:
        eventPostalCode = eventsAvailable.get(event).get("event_postalcode")
        eventsAndDistances[event] = distanceUtility.query_postal_code(teamPostalCode, eventPostalCode)
    return eventsAndDistances

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


