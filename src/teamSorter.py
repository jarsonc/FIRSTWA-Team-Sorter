from constants import *
from getFLLInfo import *
from getFTCInfo import *
from util import *

import sys

def main(programSelection):
    sys.tracebacklimit = 0
    if programSelection is FLL_CHALLENGE:
        print("Sorting FLL teams and events")
        if checkDataExists(programSelection):
            if promptForRerun():
                print("Historical data exists, using existing data instead of reimport")
                eventsAvailable = importExistingEventsFile(programSelection)
                teamsWithEventDistances = importExistingTeamsFile(programSelection)
            else:
                print("Scraping teams and events")
                eventsAvailable = importFLLEvents(programSelection)
                teamsWithEventDistances = parseFLLTeams(eventsAvailable, programSelection)
        else:
            eventsAvailable = importFLLEvents(programSelection)
            teamsWithEventDistances = parseFLLTeams(eventsAvailable, programSelection)
    elif programSelection is FRC:
        print("FRC not currently supported (and/or needed)")
        return
    elif programSelection is FTC:
        print("Sorting FTC teams and events")
        eventsAvailable = importFTCEvents()
        teamsWithEventDistances = parseFTCTeams(eventsAvailable, programSelection)
    sortAndSave(teamsWithEventDistances, eventsAvailable, programSelection)
    
def sortAndSave(teamsWithEventDistances, eventsAvailable, programSelection):
    eventsWithTeamList = sortTeams(teamsWithEventDistances, eventsAvailable)
    if checkAlreadySorted(programSelection):
        if not promptForReSort():
            print("No action taken. Original sort preserved")
    convertDictToFile(eventsWithTeamList, GENERATED_LIST_FILE, programSelection)
    print("Finished sorting and saving teams!")
    print(printMetricData())
    #print(printAnomalies(teamsWithEventDistances))

def printAnomalies(teamsWithEventDistances):
    for team, distance in METRIC_DATA.get(FLAGGED_TEAMS):
        print("Team: ", team, "flagged for distance: ", distance)
        print("Assigned to: ", list(teamsWithEventDistances.get(team).keys())[list(teamsWithEventDistances.get(team).values()).index(distance)])
        print(teamsWithEventDistances.get(team))
    print(METRIC_DATA.get(FLAGGED_TEAMS))
# FLL
main(PROGRAM_TYPES[0])
# FRC
#main(PROGRAM_TYPES[1])
# FTC
#main(PROGRAM_TYPES[2])