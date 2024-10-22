import random
import contextily as cx
import geodatasets
import geopandas
import matplotlib.pyplot as plt
import pandas as pd
import pgeocode

from ast import literal_eval
from constants import PANDAS_EVENT_DATAFRAME_COLUMN_TITLE, PANDAS_LAT_DATAFRAME_COLUMN_TITLE, PANDAS_LON_DATAFRAME_COLUMN_TITLE, PANDAS_TEAM_DATAFRAME_COLUMN_TITLE
from geodatasets import get_path

DEFAULT_DISTANCE = 1.0
DEFAULT_TEAM = 9999999
DEFAULT_LAT_LON = {'lat': 0.0, 'lon': 0.0}

FURTHEST_DISTANCE_METRIC = "Team farthest away from their event: "
FIRST_CHOICE_EVENT_TEAMS = "Teams assigned to closest event:"
SECOND_CHOICE_EVENT_TEAMS = "Teams assigned to SECOND closest event:"
FLAGGED_TEAMS = "Teams over 120 miles away from their assigned event:" #NOTE: This needs to be updated with the below variable
DISTANCE_TO_FLAG = 120

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

def printAnomalies(teamsWithEventDistances):
    for team, distance in METRIC_DATA.get(FLAGGED_TEAMS):
        print("Team: ", team, "flagged for distance: ", distance)
        print("Assigned to: ", list(teamsWithEventDistances.get(team).keys())[list(teamsWithEventDistances.get(team).values()).index(distance)])
        print(teamsWithEventDistances.get(team))
    print(METRIC_DATA.get(FLAGGED_TEAMS))

def generateMap(eventsWithTeamList, allTeams, allTeamData):
    allTeamLocations = []
    teamEventPairs = {}
    for event in eventsWithTeamList:
        teamList = eventsWithTeamList.get(event)
        for team in teamList:
            teamEventPairs[team[0]] = event
    for team in allTeams:
        teamLatLon = allTeamData.get(team).get('location')[0]
        if teamLatLon == DEFAULT_LAT_LON:
            teamLatLon = guessLocation(allTeamData, team)
        assignedEvent = teamEventPairs[team]
        teamLocation = (team, float(teamLatLon.get("lat")), float(teamLatLon.get("lon")), assignedEvent)
        allTeamLocations.append(teamLocation)
    df = pd.DataFrame(allTeamLocations, columns=[PANDAS_TEAM_DATAFRAME_COLUMN_TITLE, PANDAS_LAT_DATAFRAME_COLUMN_TITLE, PANDAS_LON_DATAFRAME_COLUMN_TITLE, PANDAS_EVENT_DATAFRAME_COLUMN_TITLE])
    gdf = geopandas.GeoDataFrame(df, geometry=geopandas.points_from_xy(df.Longitude, df.Latitude), crs="EPSG:4326")
    df_wm = gdf.to_crs(epsg=3857)
    ax = df_wm.plot(marker='o', column=PANDAS_EVENT_DATAFRAME_COLUMN_TITLE, categorical=True,
             markersize=10, legend=True, legend_kwds={'loc': 'best'})
    cx.add_basemap(ax)
    plt.show()
    return df

def guessLocation(allTeams, team):
    nomi = pgeocode.Nominatim('us')
    if allTeams.get(team).get('team_postalcode') == "98705": #Known bugged zip code in FIRST's system
        query = nomi.query_postal_code("98075")
    else:
        query = nomi.query_postal_code(allTeams.get(team).get('team_postalcode'))
    teamLatLon = {
        "lat": query["latitude"],
        "lon": query["longitude"]
    }
    return teamLatLon
    
def emptyPrompt():
    input("Press Enter to continue...")