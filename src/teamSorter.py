from constants import *
from getFLLInfo import *
from getFTCInfo import *
from sortingAlgs import sortTeams
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
                allTeams = importExistingTeamsFile(programSelection)
                teamsWithAllEventDistances = importExistingTeamsWithAllEventDistancesFile(programSelection)
            else:
                print("Scraping teams and events")
                eventsAvailable = importFLLEvents(programSelection)
                allTeams = importFLLTeams(programSelection)
                teamsWithAllEventDistances = parseFLLTeams(allTeams, eventsAvailable, programSelection)
        else:
            eventsAvailable = importFLLEvents(programSelection)
            allTeams = importFLLTeams(programSelection)
            teamsWithAllEventDistances = parseFLLTeams(allTeams, eventsAvailable, programSelection)
    elif programSelection is FRC:
        print("FRC not currently supported (and/or needed)")
        return
    elif programSelection is FTC:
        print("Sorting FTC teams and events")
        eventsAvailable = importFTCEvents()
        teamsWithAllEventDistances = parseFTCTeams(eventsAvailable, programSelection)
    sortAndSave(teamsWithAllEventDistances, eventsAvailable, programSelection, allTeams)
    
def sortAndSave(teamsWithEventDistances, eventsAvailable, programSelection, allTeams):
    eventsWithTeamList = sortTeams(teamsWithEventDistances, eventsAvailable)
    if checkAlreadySorted(programSelection):
        if not promptForReSort():
            print("No action taken. Original sort preserved")
    convertDictToFile(eventsWithTeamList, GENERATED_LIST_FILE, programSelection)
    print("Finished sorting and saving teams!")
    print(printMetricData())
    generateMap(eventsWithTeamList, allTeams)

# FLL
main(PROGRAM_TYPES[0])
