DEFAULT_DISTANCE = 1.0
DEFAULT_TEAM = 9999999

FURTHEST_DISTANCE_METRIC = "Team farthest away from their event: "
FIRST_CHOICE_EVENT_TEAMS = "Teams assigned to closest event:"
SECOND_CHOICE_EVENT_TEAMS = "Teams assigned to SECOND closest event:"
FLAGGED_TEAMS = "Teams over 50 miles away from their assigned event:" #NOTE: This needs to be updated with the below variable
DISTANCE_TO_FLAG = 50

WEIRD_TEAMS = "Teams that are assigned to their 3rd or greater event, but still in the 50 mile radius"

METRIC_DATA = {
    FURTHEST_DISTANCE_METRIC: (DEFAULT_TEAM, DEFAULT_DISTANCE),
    FIRST_CHOICE_EVENT_TEAMS: [],
    SECOND_CHOICE_EVENT_TEAMS: [],
    FLAGGED_TEAMS: [],
    WEIRD_TEAMS: []
} 

def printMetricData():
    print("Teams with their first choice event: ", len(METRIC_DATA[FIRST_CHOICE_EVENT_TEAMS]))
    print(FIRST_CHOICE_EVENT_TEAMS, METRIC_DATA[FIRST_CHOICE_EVENT_TEAMS])
    print("Teams with their second choice event: ", len(METRIC_DATA[SECOND_CHOICE_EVENT_TEAMS]))
    print(SECOND_CHOICE_EVENT_TEAMS, METRIC_DATA[SECOND_CHOICE_EVENT_TEAMS])
    print("Flagged teams: ", len(METRIC_DATA[FLAGGED_TEAMS]))
    print(FLAGGED_TEAMS, METRIC_DATA[FLAGGED_TEAMS])
    print("Weird teams: ", len(METRIC_DATA[WEIRD_TEAMS]))
    print(WEIRD_TEAMS, METRIC_DATA[WEIRD_TEAMS])