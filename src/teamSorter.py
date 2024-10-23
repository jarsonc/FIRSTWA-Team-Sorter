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
        if promptForInputSource():
            isManual = False
            if checkDataExists(programSelection):
                if promptForRerun():
                    print("Historical data exists, using existing data instead of reimport")
                    eventsAvailable = importExistingEventsFile(programSelection)
                    allTeams = importExistingWebsiteTeamsFile(programSelection)
                    teamsWithAllEventDistances = importExistingWebsiteTeamsWithAllEventDistancesFile(programSelection)
                else:
                    print("Scraping teams and events")
                    eventsAvailable = importFLLEvents(programSelection)
                    allTeams = importFLLTeams(programSelection)
                    teamsWithAllEventDistances = parseFLLTeams(allTeams, eventsAvailable, programSelection, True)
            else:
                    print("Scraping teams and events")
                    eventsAvailable = importFLLEvents(programSelection)
                    allTeams = importFLLTeams(programSelection)
                    teamsWithAllEventDistances = parseFLLTeams(allTeams, eventsAvailable, programSelection, True)
        else:
            isManual = True
            if checkDataExists(programSelection):
                if promptForRerun():
                    print("Historical data exists, using existing data instead of reimport")
                    eventsAvailable = importExistingEventsFile(programSelection)
                    allTeams = importExistingManualTeamsFile(programSelection)
                    teamsWithAllEventDistances = importExistingManualTeamsWithAllEventDistancesFile(programSelection)
                else:
                    print("Scraping events - Current expected file does NOT have event data.")
                    eventsAvailable = importFLLEvents(programSelection)
                    print("Please select a file for team selection")
                    allTeams = getTeamsFromInput(programSelection)
                    teamsWithAllEventDistances = parseFLLTeams(allTeams, eventsAvailable, programSelection, False)
            else:
                print("Scraping events - Current expected file does NOT have event data.")
                eventsAvailable = importFLLEvents(programSelection)
                print("Please select a file for team selection")
                allTeams = getTeamsFromInput(programSelection)
                teamsWithAllEventDistances = parseFLLTeams(allTeams, eventsAvailable, programSelection, False)

    elif programSelection is FRC:
        print("FRC not currently supported (and/or needed)")
        return
    elif programSelection is FTC:
        print("Sorting FTC teams and events")
        eventsAvailable = importFTCEvents()
        teamsWithAllEventDistances = parseFTCTeams(eventsAvailable, programSelection)
    sortAndSave(teamsWithAllEventDistances, eventsAvailable, programSelection, allTeams, isManual)
    
def sortAndSave(teamsWithEventDistances, eventsAvailable, programSelection, allTeams, isManual):
    eventsWithTeamList = sortTeams(teamsWithEventDistances, eventsAvailable)
    if checkAlreadySorted(programSelection):
        if not promptForReSort():
            print("No action taken. Original sort preserved")
    for event in eventsWithTeamList:
        for team, distance in eventsWithTeamList[event]:
            allTeams[team][ASSINGNED_EVENT_FIELD] = event
            print(allTeams[team])
    convertDictToFile(eventsWithTeamList, GENERATED_LIST_FILE, programSelection)
    convertDictToFile(allTeams, GENERATED_TEAM_OUTPUT_WITH_EVENTS, programSelection)
    print("Finished sorting and saving teams!")
    printMetricData()
    if isManual:
        print("Manual search does NOT have location field. Scraping FIRST website")
        allTeamData = importFLLTeams(PROGRAM_TYPES[0])
        generateMap(eventsWithTeamList, allTeams, allTeamData)
    else:
        generateMap(eventsWithTeamList, allTeams, allTeams)

# FLL
main(PROGRAM_TYPES[0])
