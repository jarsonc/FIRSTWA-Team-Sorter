from constants import DEFAULT_CAPACITY, EVENT_POSTAL_CODE_DATATYPE, FTC_EVENTS_URL, FTC_TEAMS_URL, LEAGUE_TOURNAMENT_SUBTYPE, TEAM_POSTAL_CODE_DATATYPE, STATE_ARG
from ftcKeys import *
from util import *

import json
import requests


def importFTCEvents():
    response = requests.get(FTC_EVENTS_URL.format(season=2023), auth=(USERNAME, PASSWORD))
    eventDataJson = json.loads(response.content.decode('utf-8'))
    completeEventData = eventDataJson["events"]
    eventsToSort = {}
    for event in completeEventData:
        if event["stateprov"] == STATE_ARG and event["typeName"] == LEAGUE_TOURNAMENT_SUBTYPE:
            postalCode = findPostalCodeByCity(event)
            event[EVENT_POSTAL_CODE_DATATYPE] = postalCode
            if CUSTOM_CAPACITY_TYPE not in event.keys():
                event["event_capacity"] = DEFAULT_CAPACITY
            eventsToSort[event["name"]] = event
    return eventsToSort


def importFTCTeams():
    response = requests.get(FTC_TEAMS_URL.format(season=2023), params={"state": STATE_ARG}, auth=(USERNAME, PASSWORD))
    teamBodyJson = json.loads(response.content.decode('utf-8'))
    numTeamsTotal = teamBodyJson["teamCountTotal"]
    availableTeams = {}
    for team in teamBodyJson["teams"]:
        if team["homeRegion"] == "USWA":
            postalCode = findPostalCodeByCity(team)
            team[TEAM_POSTAL_CODE_DATATYPE] = postalCode
            availableTeams[team["teamNumber"]] = team
    pageNum = 2
    processedTeams = len(availableTeams.keys())
    while processedTeams < numTeamsTotal:
        response = requests.get(FTC_TEAMS_URL.format(season=2023), params={"state": STATE_ARG, "page": pageNum}, auth=(USERNAME, PASSWORD))
        teamBodyJson = json.loads(response.content.decode('utf-8'))
        for team in teamBodyJson["teams"]:
            processedTeams += 1
            if team["homeRegion"] == "USWA":
                postalCode = findPostalCodeByCity(team)
                team[TEAM_POSTAL_CODE_DATATYPE] = postalCode
                availableTeams[team["teamNumber"]] = team
        pageNum += 1
    return availableTeams

def parseFTCTeams(eventsAvailable, programSelection):
    teamsToSort = importFTCTeams()
    print("Assigning ", len(teamsToSort), " to ", len(eventsAvailable), " events with ", len(eventsAvailable) * DEFAULT_CAPACITY, " spots")
    teamsWithEventDistances = {}
    number = 1
    for team in teamsToSort:
        teamsWithEventDistances[team] = dict(sorted(findDistanceByPostalCode(teamsToSort.get(team), eventsAvailable).items(), key=lambda item: item[1]))
        print("Team: ",  "{:<5}".format(team), " | ", number, " out of: ", len(teamsToSort.keys()))
        number += 1
    convertDictToFile(teamsWithEventDistances, GENERATED_TEAMS_WITH_DISTANCES_FILE, programSelection)
    return teamsWithEventDistances
