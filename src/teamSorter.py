from constants import *
from getFLLInfo import *
from getFTCinfo import *
from util import *

def main(programSelection):
    if programSelection is FLL_CHALLENGE:
        print("Sorting FLL teams and events")
        eventsAvailable = importFLLEvents()
        teamsWithEventDistances = parseFLLTeams(eventsAvailable)
    elif programSelection is FRC:
        print("FRC not currently supported (and/or needed)")
        return
    elif programSelection is FTC:
        print("Working on FTC too")
        eventsAvailable = importFTCEvents()
        print(eventsAvailable)
        teamsAvailable = importFTCTeams()
        print(teamsAvailable)
        return
    eventsWithTeamList = sortTeams(teamsWithEventDistances, eventsAvailable)
    convertDictToFile(eventsWithTeamList, GENERATED_LIST_FILE)

# FLL
#main(PROGRAM_TYPES[0])
# FRC
# main(PROGRAM_TYPES[1])
# FTC
main(PROGRAM_TYPES[2])