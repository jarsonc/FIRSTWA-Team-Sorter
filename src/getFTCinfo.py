import json
from constants import FTC_EVENTS_URL, FTC_TEAMS_URL
from ftcKeys import *

import requests

def importFTCEvents():
    response = requests.get(FTC_EVENTS_URL.format(season=2023), auth=(USERNAME, PASSWORD))
    eventDataJson = json.loads(response.content.decode('utf-8'))
    availableEvents = eventDataJson["events"]
    return availableEvents

def importFTCTeams():
    response = requests.get(FTC_TEAMS_URL.format(season=2023), params={"state": "WA"}, auth=(USERNAME, PASSWORD))
    teamBodyJson = json.loads(response.content.decode('utf-8'))
    availableTeams = {}
    for team in teamBodyJson["teams"]:
        availableTeams[team] = teamBodyJson["teams"]["team"]
    pageNum = 2
    while len(availableTeams.keys()):
        response = requests.get(FTC_TEAMS_URL.format(season=2023), params={"state": "WA", "page": pageNum}, auth=(USERNAME, PASSWORD))
        for team in teamBodyJson["teams"]:
            availableTeams[team] = teamBodyJson["teams"]["team"]
        pageNum += 1

    return availableTeams