CUSTOM_CAPACITY_TYPE = "event_capacity"
DEFAULT_CAPACITY = 40
EVENT_POSTAL_CODE_DATATYPE = "event_postalcode"
FLL_CHALLENGE = "FIRST LEGO League Challenge"
FRC = "FIRST Robotics Competition"
FTC = "FIRST Tech Challenge"
LEAGUE_TOURNAMENT_SUBTYPE = "League Tournament"
PROGRAM_TYPES = [FLL_CHALLENGE, FRC, FTC]
QUALIFYING_EVENT_SUBTYPE = "Qualifying Event"
STATE_ARG = "WA"
TEAM_POSTAL_CODE_DATATYPE = "team_postalcode"
TEAM_POSTAL_CODE_DATATYPE_MANUAL_INPUT = "Team Postal Code"
WEEKEND_DAYS = ["Sunday", "Saturday"]

FIRST_WA_TEAMS_URL = "https://es02.firstinspires.org/teams/_search?size={numTeams:n}"
FIRST_WA_TEAMS_POSTFIX = "&from=0&source_content_type=application/json&source={%22query%22:{%22bool%22:{%22must%22:[{%22bool%22:{%22should%22:[{%22match%22:{%22team_type%22:%22FLL%22}}]}},{%22bool%22:{%22should%22:[{%22match%22:{%22fk_program_seasons%22:%22335%22}},{%22match%22:{%22fk_program_seasons%22:%22333%22}},{%22match%22:{%22fk_program_seasons%22:%22337%22}},{%22match%22:{%22fk_program_seasons%22:%22331%22}}]}},{%22match%22:{%22team_country%22:%22USA%22}},{%22match%22:{%22team_stateprov%22:%22WA%22}}]}},%22sort%22:%22team_number_yearly%22}"
FIRST_WA_EVENTS_URL = "https://es02.firstinspires.org/events/_search?size={numEvents:n}"
FIRST_WA_EVENTS_POSTFIX = "&from=0&source_content_type=application/json&source={%22query%22:{%22bool%22:{%22must%22:[{%22bool%22:{%22should%22:[{%22match%22:{%22event_type%22:%22FLL%22}}]}},{%22range%22:{%22date_end%22:{%22gte%22:%222024-10-01%22,%22lte%22:%222025-01-01%22}}},{%22match%22:{%22event_country%22:%22USA%22}},{%22match%22:{%22event_stateprov%22:%22WA%22}}]}},%22sort%22:%22event_name.raw%22}"


GENERATED_EVENT_FILE = "events.csv"
GENERATED_FILE_PATH_ROOT = "./generatedFiles/"
GENERATED_LIST_FILE = "OUTPUT_eventsWithTeamList.csv"
GENERATED_TEAM_OUTPUT_WITH_EVENTS = "OUTPUT_modifiedTeamListWithEventAssignment.csv"
GENERATED_TEAMS_FROM_WEBSITE_FILE = "INPUT_website_teamData.csv"
GENERATED_TEAMS_FROM_MANUAL_FILE = "INPUT_manual_teamData.csv"
GENERATED_WEBSITE_TEAMS_WITH_ALL_EVENT_DISTANCES = "GENERATED_website_teamsWithAllEventDistances.csv"
GENERATED_MANUAL_TEAMS_WITH_ALL_EVENT_DISTANCES = "GENERATED_manual_teamsWithAllEventDistances.csv"

ASSINGNED_EVENT_FIELD = "Assigned Event"

FTC_EVENTS_URL = "http://ftc-api.firstinspires.org/v2.0/{season:n}/events"
FTC_TEAMS_URL = "http://ftc-api.firstinspires.org/v2.0/{season}/teams"

PANDAS_EVENT_DATAFRAME_COLUMN_TITLE = "Assigned Event"
PANDAS_LAT_DATAFRAME_COLUMN_TITLE = "Latitude"
PANDAS_LON_DATAFRAME_COLUMN_TITLE = "Longitude"
PANDAS_TEAM_DATAFRAME_COLUMN_TITLE = "Team Number"