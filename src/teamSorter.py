from constants import *
from getFLLInfo import *
from getFTCinfo import *
from util import *

import sys

def main(programSelection):
    sys.tracebacklimit = 0
    if programSelection is FLL_CHALLENGE:
        print("Sorting FLL teams and events")
        if checkAlreadySorted(programSelection):
            if promptForRerun():
                print("Historical data exists, using existing data instead of reimport")
                eventsAvailable = importExistingEventsFile(programSelection)
                teamsWithEventDistances = importExistingTeamsFile(programSelection)
            else:
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
    eventsWithTeamList = sortTeams(teamsWithEventDistances, eventsAvailable)
    convertDictToFile(eventsWithTeamList, GENERATED_LIST_FILE, programSelection)

# FLL
main(PROGRAM_TYPES[0])
# FRC
# main(PROGRAM_TYPES[1])
# FTC
# main(PROGRAM_TYPES[2])

def promptForRerun():
    inputPrompt = "Existing team/event list found. Use existing data? (Y/N)"
    return (input(inputPrompt).lower() == "y" or "yes")