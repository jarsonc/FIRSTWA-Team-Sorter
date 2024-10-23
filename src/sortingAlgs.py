from operator import itemgetter
from typing import OrderedDict

from constants import CUSTOM_CAPACITY_TYPE
from metrics import *

def sortTeams(teamsWithEventDistances, eventsAvailable):
    eventsWithTeamList = {}
    preference = {}
    for team in teamsWithEventDistances:
        sortedEventList = OrderedDict(sorted(teamsWithEventDistances.get(team).items(), key=lambda item: item[1]))
        event, nthChoiceEvent = findEvent(sortedEventList, eventsWithTeamList, team, teamsWithEventDistances, eventsAvailable, preference, 1)
        addPreferenceMetric(nthChoiceEvent, team, teamsWithEventDistances.get(team).get(event), teamsWithEventDistances.get(team))
    return eventsWithTeamList

def findEvent(sortedEventList, eventsWithTeamList, team, teamsWithEventDistances, eventsAvailable, preference, nthChoiceEvent):
    for event in sortedEventList:
        if event not in eventsWithTeamList:
            print("Assigning: ", "{:<5}".format(team), " to new event", event , "at distance", "{:.2f}".format(teamsWithEventDistances.get(team).get(event)))
            eventsWithTeamList[event] = [(team, teamsWithEventDistances.get(team).get(event))]
            preference[team] = nthChoiceEvent
            break
        elif len(eventsWithTeamList[event]) < eventsAvailable.get(event).get(CUSTOM_CAPACITY_TYPE):
            print("Assigning: ", "{:<5}".format(team), " to existing event", event , "at distance", "{:.2f}".format(teamsWithEventDistances.get(team).get(event)))
            eventsWithTeamList.get(event).append((team, teamsWithEventDistances.get(team).get(event)))
            eventsWithTeamList[event] = sorted(eventsWithTeamList.get(event),key=itemgetter(1))
            preference[team] = nthChoiceEvent
            break
        else:
            currentTeamDistance = teamsWithEventDistances.get(team).get(event)
            assignedTeams = sorted(eventsWithTeamList.get(event),key=itemgetter(1))
            for assignedTeam, assignedTeamDistance in assignedTeams:
                currentTeamPreference = list(sortedEventList.keys()).index(event)
                assignedTeamPreference = preference[assignedTeam]
                # If during the course of sorting, the event is full, we double check that there is no team farther away AND lower preferenced (i.e, if this is our 1st preference, we should get in over a 2nd preferenced team)
                if assignedTeamDistance > currentTeamDistance and currentTeamPreference < assignedTeamPreference:
                    eventsWithTeamList.get(event).remove((assignedTeam, assignedTeamDistance))
                    preference.pop(assignedTeam)
                    print("Reallocating: ", "{:<5}".format(team), " to ", event , "at distance", "{:.2f}".format(teamsWithEventDistances.get(team).get(event)))
                    eventsWithTeamList.get(event).append((team, currentTeamDistance))
                    preference[team] = currentTeamPreference
                    print("Rerunning sort for removed team: ", assignedTeam)
                    event, nthChoiceEvent = findEvent(sortedEventList, eventsWithTeamList, assignedTeam, teamsWithEventDistances, eventsAvailable, preference, 1)
                    return event, nthChoiceEvent
            nthChoiceEvent += 1
    return event, nthChoiceEvent

def addPreferenceMetric(nthChoiceEvent, team, distance, allEventDistances):
    if nthChoiceEvent == 1:
        METRIC_DATA[FIRST_CHOICE_EVENT_TEAMS].append(team)
    elif nthChoiceEvent == 2:
        METRIC_DATA[SECOND_CHOICE_EVENT_TEAMS].append(team)
    elif nthChoiceEvent >= 3 and distance > DISTANCE_TO_FLAG:
        print("Flagging team: ", team, "with distance: ", distance, " which is their nth choice: ", nthChoiceEvent)
        print(allEventDistances)
        METRIC_DATA[FLAGGED_TEAMS].append((team, distance))
    else:
        METRIC_DATA[WEIRD_TEAMS].append(team)

