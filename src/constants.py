CUSTOM_CAPACITY_TYPE = "event_capacity"
DEFAULT_CAPACITY = 50
FLL_CHALLENGE = "FIRST LEGO League Challenge"
FRC = "FIRST Robotics Competition"
FTC = "FIRST Tech Challenge"
PROGRAM_TYPES = [FLL_CHALLENGE, FRC, FTC]
QUALIFYING_EVENT_SUBTYPE = "Qualifying Event"
WEEKEND_DAYS = ["Sunday", "Saturday"]

FIRST_WA_TEAMS_URL = "https://es02.firstinspires.org/teams/_search?size={numTeams:n}"
FIRST_WA_TEAMS_POSTFIX = "&from=0&source_content_type=application/json&source={%22query%22:{%22bool%22:{%22must%22:[{%22bool%22:{%22should%22:[{%22match%22:{%22team_type%22:%22FLL%22}}]}},{%22bool%22:{%22should%22:[{%22match%22:{%22fk_program_seasons%22:%22323%22}},{%22match%22:{%22fk_program_seasons%22:%22321%22}},{%22match%22:{%22fk_program_seasons%22:%22325%22}},{%22match%22:{%22fk_program_seasons%22:%22319%22}}]}},{%22match%22:{%22team_country%22:%22USA%22}},{%22match%22:{%22team_stateprov%22:%22WA%22}}]}},%22sort%22:%22team_nickname.raw%22}"
FIRST_WA_EVENTS_URL = "https://es02.firstinspires.org/events/_search?size={numEvents:n}"
FIRST_WA_EVENTS_POSTFIX = "&from=0&source_content_type=application/json&source={%22query%22:{%22bool%22:{%22must%22:[{%22bool%22:{%22should%22:[{%22match%22:{%22event_type%22:%22FLL%22}}]}},{%22bool%22:{%22should%22:[{%22match%22:{%22fk_program_seasons%22:%22323%22}},{%22match%22:{%22fk_program_seasons%22:%22321%22}},{%22match%22:{%22fk_program_seasons%22:%22325%22}},{%22match%22:{%22fk_program_seasons%22:%22319%22}}]}},{%22range%22:{%22date_end%22:{%22gte%22:%222023-01-01%22,%22lte%22:%222025-05-07%22}}},{%22match%22:{%22event_country%22:%22USA%22}},{%22match%22:{%22event_stateprov%22:%22WA%22}}]}},%22sort%22:%22event_name.raw%22}"

GENERATED_FILE_PATH_ROOT = ".././generatedFiles/"
GENERATED_LIST_FILE = "eventsWithTeamList.csv"
TEAMS_WITH_DISTANCES_FILE = "teamsWithEventDistances.csv"

FTC_EVENTS_URL = "http://ftc-api.firstinspires.org/v2.0/{season:n}/events"
FTC_TEAMS_URL = "http://ftc-api.firstinspires.org/v2.0/{season}/teams"