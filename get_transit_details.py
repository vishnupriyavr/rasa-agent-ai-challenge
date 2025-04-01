import googlemaps
import os
import datetime
import dotenv

from dotenv import load_dotenv
load_dotenv("/Users/vishnupriyavr/Documents/rasa-agent-ai-challenge/.env")

import requests
import json
import polyline

from geopy.geocoders import GoogleV3
from geopy.distance import geodesic

import itertools

API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

geolocator = GoogleV3(api_key=API_KEY)

# Replace with your actual API key
gmaps = googlemaps.Client(key=os.getenv("GOOGLE_MAPS_API_KEY"))

def get_dict_from_list(list_of_dicts, key, param):

    for dictionary in list_of_dicts:
        if key in dictionary:
            #print(key)
            #print(dictionary[key].get(param))
            if isinstance(dictionary[key], list):
                return dictionary[key][0].get(param)
            
            return dictionary[key].get(param)
    return None

def get_location_name(latitude_list, longitude_list):
    #coordinates = f"{latitude}, {longitude}"
    location_list = []
    try:
        for x, y in itertools.product(latitude_list, longitude_list):
            location = geolocator.reverse((x,y), exactly_one=True)
            print(location.address)
            location_list.append(location.address)
        return location_list
    except Exception as e:
        return f"Error: {e}"
    
def intermediate_stop_details(directions_result):
    intermediate_stops = {}
    # Example usage:
    # for dict in directions_result:
    #     for polyline in dict["legs"]["polyline"]:
    #         print(polyline["points"])
    #         intermediate_stops.append(polyline["points"])

    
    legs_dict = {}
    steps_dict = {}
    point_list = []
    html_instruction_list = []

    for result in directions_result:
        legs = result['legs']
        legs_dict["legs"] = legs
        #print(legs_dict)

    for leg in legs_dict["legs"]:
        steps = leg["steps"]
        steps_dict["steps"] = steps
        print(steps_dict)
        
    for step in steps_list:
        point = step["polyline"]["points"]
        html_instruction = step["html_instructions"]
        point_list.append(point)
        html_instruction_list.append(html_instruction)
        

    intermediate_stops["legs_list"] = legs_list
    intermediate_stops["steps_list"] = steps_list
    intermediate_stops["point_list"] = point_list
    intermediate_stops["html_instruction_list"] = html_instruction_list

    decoded_polyline_list = []
    for each in intermediate_stops["point_list"]:
        decoded_polyline = polyline.decode(each)
        decoded_polyline_list.append(decoded_polyline)

    print(decoded_polyline_list)

    lat, lang = zip(*decoded_polyline_list)

    intermediate_stops = get_location_name(lat, lang)

    return intermediate_stops

def get_current_location():
    url = f"https://www.googleapis.com/geolocation/v1/geolocate?key={API_KEY}"
    headers = {'Content-Type': 'application/json'}
    payload = {}
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        location_data = response.json()
        if 'location' in location_data:
            latitude = location_data['location']['lat']
            longitude = location_data['location']['lng']
            accuracy = location_data['accuracy']
            return latitude, longitude, accuracy
        else:
            print("Location data not found in response.")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None
    except json.JSONDecodeError:
        print("Failed to decode JSON response.")
        return None

def nearest_stop_details(radius):
    # Coordinates for the search location

    current_location = get_current_location()
    if current_location:
        latitude, longitude, accuracy = current_location
        print(f"Latitude: {latitude}, Longitude: {longitude}, Accuracy: {accuracy} meters")
    else:
        print("Could not retrieve location.")
    location = (latitude, longitude)

    nearest_places_list = []
    # Search for bus stops within a 1000-meter radius
    places_result = gmaps.places_nearby(location=location, radius=radius, type='bus_station|transit_station')

    #print(places_result)
    # Print the names of the bus stops
    for place in places_result.get('results', []):
        #print(place.get('name'))
        nearest_places_list.append(place.get('name'))

    # Handle pagination if there are more than 20 results
    while 'next_page_token' in places_result:
        places_result = gmaps.places_nearby(page_token=places_result['next_page_token'])
        for place in places_result.get('results', []):
            #print(place.get('name'))
            nearest_places_list.append(place.get('name'))

    return nearest_places_list
    
def get_transit_route(origin=None, destination=None, transit_mode=None, departure_time=None, get_arrival_time=False,
                      get_fare_details=False, get_nearest_stop=False, get_intermediate_stops=False):

    # Define origin and destination

    now = datetime.datetime.now()
    route = None

    # Specify transit mode and other parameters
    future_time = now + datetime.timedelta(minutes=5)
    directions_result = gmaps.directions(
        origin,
        destination,
        mode="transit",
        transit_mode="bus",
        departure_time=departure_time, # Specify departure time
        #arrival_time="2025-04-01T10:00:00" # Or arrival time
    )

    # # Print the results (you can parse and analyze the data as needed)
    print(directions_result)

    # directions_result = [{'bounds': {'northeast': {'lat': 13.0731552, 'lng': 80.26939510000001}, 'southwest': {'lat': 12.9807135, 'lng': 80.1882342}}, 'copyrights': 'Powered by Google, ©2025 Google', 'fare': {'currency': 'INR', 'text': '₹17.00', 'value': 17}, 'legs': [{'arrival_time': {'text': '1:14\u202fPM', 'time_zone': 'Asia/Calcutta', 'value': 1743407077}, 'departure_time': {'text': '12:08\u202fPM', 'time_zone': 'Asia/Calcutta', 'value': 1743403085}, 'distance': {'text': '16.1 km', 'value': 16086}, 'duration': {'text': '1 hour 7 mins', 'value': 3992}, 'end_address': 'Egmore, Chennai, Tamil Nadu, India', 'end_location': {'lat': 13.0731365, 'lng': 80.2609207}, 'start_address': 'Nanganallur, Chennai, Tamil Nadu, India', 'start_location': {'lat': 12.9807182, 'lng': 80.1882342}, 'steps': [{'distance': {'text': '0.3 km', 'value': 309}, 'duration': {'text': '4 mins', 'value': 252}, 'end_location': {'lat': 12.9829804, 'lng': 80.1888592}, 'html_instructions': 'Walk to Chithambaram Stores', 'polyline': {'points': 'ohfnAmwlhN@K{BGE?qBC_DKw@CDuA'}, 'start_location': {'lat': 12.9807182, 'lng': 80.1882342}, 'steps': [{'distance': {'text': '6 m', 'value': 6}, 'duration': {'text': '1 min', 'value': 5}, 'end_location': {'lat': 12.9807135, 'lng': 80.1882906}, 'html_instructions': 'Head <b>east</b> on <b>6th Main Rd</b> toward <b>46th St</b>', 'polyline': {'points': 'ohfnAmwlhN@K'}, 'start_location': {'lat': 12.9807182, 'lng': 80.1882342}, 'travel_mode': 'WALKING'}, {'distance': {'text': '0.3 km', 'value': 256}, 'duration': {'text': '3 mins', 'value': 209}, 'end_location': {'lat': 12.9830122, 'lng': 80.1884292}, 'html_instructions': 'Turn <b>left</b> at Nanganallur Chennai onto <b>4th Main Rd</b><div style="font-size:0.9em">Pass by BALAJI ENTERPRISES (on the right in 39m)</div>', 'maneuver': 'turn-left', 'polyline': {'points': 'mhfnAywlhN{BGE?qBC_DKw@C'}, 'start_location': {'lat': 12.9807135, 'lng': 80.1882906}, 'travel_mode': 'WALKING'}, {'distance': {'text': '47 m', 'value': 47}, 'duration': {'text': '1 min', 'value': 38}, 'end_location': {'lat': 12.9829804, 'lng': 80.1888592}, 'html_instructions': 'Turn <b>right</b> at the pharmacy onto <b>1st Main Rd</b><div style="font-size:0.9em">Pass by Veera mobiles (on the right in 21m)</div><div style="font-size:0.9em">Destination will be on the left</div>', 'maneuver': 'turn-right', 'polyline': {'points': 'yvfnAuxlhNDuA'}, 'start_location': {'lat': 12.9830122, 'lng': 80.1884292}, 'travel_mode': 'WALKING'}], 'travel_mode': 'WALKING'}, {'distance': {'text': '12.8 km', 'value': 12771}, 'duration': {'text': '42 mins', 'value': 2527}, 'end_location': {'lat': 13.05684, 'lng': 80.25674099999999}, 'html_instructions': 'Bus towards Broadway Bus Terminal', 'polyline': {'points': 'awfnAo{lhNL@@O@aA@m@@qB?k@?Q@g@BeARyEQAu@EgAIMAy@G]Cy@EIAGAsBMc@EsAOiAQi@Ie@GYEm@Ig@K{@Oq@K_BSyAU{@O[EaAOkAOSAHy@XoBPqA^aDBWVyANy@BQNk@DUVgADSJg@FO?ADONq@aBa@iAQwCc@mASQEE?SEk@IMCyASYKICICg@M[OOGOKk@SYQWOQKIGMKy@u@MKc@[YYWKQG[EWKGCq@O]GC?UA]CIACAAACCGIKOCEACCECQAe@?_A?AAM?G?EEoAGeBBi@NsBMECAAA?CAABa@Hg@\\aCV_BL{@DUCCAECCACAC@GXyGm@M]Ga@Gw@M}AQQCq@K{BYgAQoAMmAQmAOaAMSEm@Iw@KOCUCy@Me@Cu@IKAa@CGAGCUKa@OYMMGIEUIKEWIc@Og@Uc@ScAa@{@_@aAc@}@]a@QEECCAE?G?IKEOE?k@EuACKAg@Ee@Cg@AECu@C_@?I?G?E?E@O?QAcA?Gg@G_@EOCUIGCUIKEIGYMsAm@SMWMWMKEGCIEGCCAEAICMCE?I?E@GBk@V[HMBI?W@U?WAWAYCu@EWEKAKCICGEMEGGECMK_@Yu@[OCEAECGAAAAAq@o@aAyAMS_@g@_@o@_@i@SYMSQYACMYU_@MQIGIKWUGGGIKQIOCIEKEMEMCKI_@AC?AScAw@iBYeAK]CK[sAMg@EMMg@EOU}@Mm@SeAUkACKSaAI[Qk@Ma@GOACCIISEKGKEISU]g@cAuAm@s@[_@_@c@_@i@AACCACCCACAE?CAM_@e@UYIMe@i@cAoAu@aAOCEAc@_@IIWUACIIIIIGIGKGKEOKQKKAG?I@G@GBMBa@Jw@Rs@RsDfAuC|@KBI@IBG?I@Q?E?M?AAI?GAEAC?EASGe@Qo@Yq@c@a@WeBkAcAq@q@a@qBuAOKcAy@yAmAk@g@i@e@q@s@]c@SUSYmAyAU_@A?m@y@IO]e@k@u@OUIK_@i@CCa@q@[m@M[Sk@U{@Ms@EY[iBMo@I[CIAEKa@EOCGe@kAaAuBuAgC}AkDQ[GO_AkAY]SUW[i@k@m@s@g@i@IIKOg@w@OUu@uAYi@o@mAIQk@oAO[i@iAWe@MWGOqAkD}A_E[y@EIYm@Yi@IOIQMUWg@CCMSQ[QSKQOSEGQWOSY_@MQmAgBMSGI{AsBQWg@s@UWIGIIMKGGA?UKIESEm@IQE_AMCA[E{Dg@OCe@IKAA?SCeC_@sAUc@G{@MSCq@IuAOWC_@Ew@K]EWEE?UCEASAoAO[Ec@E]EOCKAa@E{@KGAw@KSEwBWSE{@KUE[CeAOMAYEc@GI?q@IWCSAe@GA?IAyAQi@IYCICgAIKA[GMCOGKEIESOWU[[_Aw@WWQOMKOIKGOIMEICOAMA[CyAKs@Gm@ESCuC_@UCQCWEo@OWIOIUIKIQIGCOKYUECGAMUSUW_@IMEGCEY_@[e@[g@i@u@_AwAc@o@YWWc@SYa@m@OYU_@MOU_@QWYa@MUMSW[[a@a@m@]i@S]u@aAMS]e@Wa@Ua@_@g@_@a@MMQMKKIGGH'}, 'start_location': {'lat': 12.983054, 'lng': 80.18887500000001}, 'transit_details': {'arrival_stop': {'location': {'lat': 13.05684, 'lng': 80.25674099999999}, 'name': 'Anandh Theatre'}, 'arrival_time': {'text': '12:54\u202fPM', 'time_zone': 'Asia/Calcutta', 'value': 1743405865}, 'departure_stop': {'location': {'lat': 12.983054, 'lng': 80.18887500000001}, 'name': 'Chithambaram Stores'}, 'departure_time': {'text': '12:12\u202fPM', 'time_zone': 'Asia/Calcutta', 'value': 1743403338}, 'headsign': 'Broadway Bus Terminal', 'line': {'agencies': [{'name': 'Metropolitan Transport Corporation', 'phone': '011 91 94450 30516', 'url': 'https://mtcbus.tn.gov.in/'}], 'short_name': '18D', 'vehicle': {'icon': '//maps.gstatic.com/mapfiles/transit/iw2/6/bus2.png', 'name': 'Bus', 'type': 'BUS'}}, 'num_stops': 19}, 'travel_mode': 'TRANSIT'}, {'distance': {'text': '2.9 km', 'value': 2880}, 'duration': {'text': '10 mins', 'value': 573}, 'end_location': {'lat': 13.07285, 'lng': 80.26201999999999}, 'html_instructions': 'Bus towards Villivakkam Bus Station', 'polyline': {'points': 'gdunAsczhNFIOKs@q@KImAmAg@c@eAoAOSyAkB_AiAQUe@m@]e@k@w@IKY[IM_@g@W]s@{@GGOQi@u@KM[a@{BuC{@cAo@}@QUY[Wg@iA}A_@i@o@y@{@kAe@o@iAqAIMo@y@[a@IKuAkBq@{@OSm@}@[c@OUKOIKEDEG_@c@k@w@UUYM]OWKy@e@BImAs@AAIEmBcAMGWMEVET[jBET[lAQp@c@vAIZo@r@IH{@~@QRaAdA_@^QPONUVURGDQDGDk@n@QRu@r@OLEFu@v@YZu@z@KLQXQ\\MXM\\IVGTK\\S`A?D@BADENENCLMp@ERENADJB'}, 'start_location': {'lat': 13.05684, 'lng': 80.25674099999999}, 'transit_details': {'arrival_stop': {'location': {'lat': 13.07285, 'lng': 80.26201999999999}, 'name': 'Adhithanar Salai Egmore Court'}, 'arrival_time': {'text': '1:12\u202fPM', 'time_zone': 'Asia/Calcutta', 'value': 1743406955}, 'departure_stop': {'location': {'lat': 13.05684, 'lng': 80.25674099999999}, 'name': 'Anandh Theatre'}, 'departure_time': {'text': '1:03\u202fPM', 'time_zone': 'Asia/Calcutta', 'value': 1743406382}, 'headsign': 'Villivakkam Bus Station', 'line': {'agencies': [{'name': 'Metropolitan Transport Corporation', 'phone': '011 91 94450 30516', 'url': 'https://mtcbus.tn.gov.in/'}], 'short_name': '27D', 'vehicle': {'icon': '//maps.gstatic.com/mapfiles/transit/iw2/6/bus2.png', 'name': 'Bus', 'type': 'BUS'}}, 'num_stops': 8}, 'travel_mode': 'TRANSIT'}, {'distance': {'text': '0.1 km', 'value': 126}, 'duration': {'text': '2 mins', 'value': 119}, 'end_location': {'lat': 13.0731365, 'lng': 80.2609207}, 'html_instructions': 'Walk to Egmore, Chennai, Tamil Nadu, India', 'polyline': {'points': 'uhxnAud{hNKb@Kd@CTOp@?@@??@?@?B@@?@AB?@A??@A@Cb@BF?@?@?@?@'}, 'start_location': {'lat': 13.0729096, 'lng': 80.26203009999999}, 'steps': [{'distance': {'text': '0.1 km', 'value': 117}, 'duration': {'text': '2 mins', 'value': 107}, 'end_location': {'lat': 13.0731552, 'lng': 80.2610021}, 'html_instructions': 'Head <b>west</b> on <b>Adithanar Rd</b><div style="font-size:0.9em">Go through 1 roundabout</div><div style="font-size:0.9em">Pass by Sanjiv Shah &amp; Associates (on the left in 26m)</div>', 'polyline': {'points': 'uhxnAud{hNKb@Kd@CTOp@?@@??@?@?B@@?@AB?@A??@A@Cb@'}, 'start_location': {'lat': 13.0729096, 'lng': 80.26203009999999}, 'travel_mode': 'WALKING'}, {'distance': {'text': '9 m', 'value': 9}, 'duration': {'text': '1 min', 'value': 12}, 'end_location': {'lat': 13.0731365, 'lng': 80.2609207}, 'html_instructions': 'Enter the roundabout', 'polyline': {'points': 'gjxnAg~zhNBF?@?@?@?@'}, 'start_location': {'lat': 13.0731552, 'lng': 80.2610021}, 'travel_mode': 'WALKING'}], 'travel_mode': 'WALKING'}], 'traffic_speed_entry': [], 'via_waypoint': []}], 'overview_polyline': {'points': 'ohfnAmwlhN@K{BGwBCwEODuAMCL@@OBoBBwEV_HgAGmDW_EWwBUsB[uCc@gHeAwAUmC_@SAHy@j@aEb@yDf@sCp@{CXmATaAaBa@iAQeFw@WEgDg@uAa@gBw@mAu@gAaAq@g@YYWKm@M_@OoAWaAGQQU_@Ew@?aAGkBGeBBi@NsBMEECAELiAt@aFRqAEIEG?KXyGm@M_AOyEo@cEk@}C_@qEm@wCa@iCSgAa@gAe@oBu@eFyB_Bo@IIAM?IKEOE?k@IaBM{BGgB@m@AkAgAMcA[gEsBe@Sa@KO?MDgA`@WBm@@o@CsBQk@S{@q@qAe@ICs@q@oCeEsAqBO]c@q@s@q@S[MYUs@Ke@ScAw@iBe@cBs@uCw@cDaA_Fi@iBWq@MWY_@aB}BiAsAeAsAIQAQu@_AiDiEUEm@i@m@m@k@]a@WSAg@JyA^gFzAuDfAi@@a@Cc@KuAk@sA{@iD}BcDwBsAeAeCuB{AyAq@y@yBsC_EuFa@q@i@iAi@gBSmAw@_EW_Ae@kAaAuBuAgC}AkDYk@yAiBcCqCq@s@s@gAeAkBiAwBoBgEe@}@yA{DyByF_@w@{@aB{@{A}B_D{A{BcB}By@kA_@_@_@]WK]KcC_@wEm@u@MgDe@gEo@sH{@mFm@qBUkAQkC]sDe@uAOcCWoC]wBSi@K[M]Us@q@wBkBy@a@cAKmCSaAIuEm@gAYe@Su@c@_@YGAMUk@u@OUuAsBiBmCc@o@YWk@}@q@gAkAgBmAgBoBwCyB}Cu@iAm@o@]YIGGHFIOK_A{@uBqBuAcBqEyFmBeCi@u@kAyAmA}AcGyHk@q@aBeCqD_F_D{DaDgEeBgCIKEDe@k@k@w@UUw@]qAq@BImAs@KG{BkAWMEVa@`Ca@bBu@hCIZo@r@eAhAeCjCcA`AYJ}@bAeA`A{@~@oAvA]f@_@v@Wt@Sr@SfAKh@]bBADJBKAKb@Oz@Or@@@@FCFEf@BN'}, 'summary': '', 'warnings': ['Walking directions are in beta. Use caution – This route may be missing sidewalks or pedestrian paths.'], 'waypoint_order': []}]

    if directions_result:
        # Access the first route
        route = directions_result[0]
        
        # Print the summary of the route
        print(route['summary'])

        # Iterate through the legs of the route
        for leg in route['legs']:
            print(f"  Distance: {leg['distance']['text']}")
            print(f"  Duration: {leg['duration']['text']}")

            # Iterate through the steps of the leg
            for step in leg['steps']:
                print(f"    {step['html_instructions']}")
                if 'transit_details' in step:
                    route = f"      Transit: {step['transit_details']} to {step['transit_details']}"
    else:
        route = "No routes found."

    fare_from_transit =  None,
    arrival_time_from_transit = None,
    nearest_stop = None

    if get_fare_details:
        fare_from_transit = get_dict_from_list(directions_result, "fare", "text")
        #return fare_from_transit
    elif get_arrival_time:
        arrival_time_from_transit = get_dict_from_list(directions_result, "legs", "arrival_time")
        #return arrival_time_from_transit.get("text")
    elif get_nearest_stop:
        nearest_stop = nearest_stop_details(radius=1000)
        #print(nearest_stop)
    # elif get_intermediate_stops:
    #     intermediate_stops = intermediate_stop_details(directions_result)
    #     print(intermediate_stops)

    return route, fare_from_transit, arrival_time_from_transit, nearest_stop