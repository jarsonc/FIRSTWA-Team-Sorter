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
    oldSort(teamsWithEventDistances, eventsAvailable, programSelection)
    
def oldSort(teamsWithEventDistances, eventsAvailable, programSelection):
    eventsWithSortedTeams = createEventKeysWithTeams(eventsAvailable, teamsWithEventDistances)
    eventsWithTeamList = sortTeams(teamsWithEventDistances, eventsAvailable)
    
    if checkAlreadySorted(programSelection):
        if promptForReSort():
            convertDictToFile(eventsWithTeamList, GENERATED_LIST_FILE, programSelection)
            print("Finished sorting and saving teams!")
            print(printMetricData())
        else:
            print("No action taken. Original sort preserved")

# FLL
main(PROGRAM_TYPES[0])
# FRC
#main(PROGRAM_TYPES[1])
# FTC
#main(PROGRAM_TYPES[2])