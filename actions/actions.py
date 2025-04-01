from typing import Any, Dict, List, Text

from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher

import requests
import os
from get_transit_details import API_KEY, get_transit_route
import datetime

from rasa.shared.nlu.training_data.message import Message
from actions.entity_extractor import duckling_entity_extractor
from rasa_sdk import Action, Tracker
from rasa_sdk.events import EventType, SlotSet
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict

from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet, SessionStarted, ActionExecuted, EventType

def parse_datetime(text: str):
    # If the text is already a date slot value extracted from Duckling,
    # we can just use it
    try:
        result = datetime.fromisoformat(text)
        return result.replace(tzinfo=None)
    except ValueError:
        pass

    # Otherwise, we need to parse the value set by the LLM
    # using Duckling
    msg = Message.build(text)
    duckling_entity_extractor.process([msg])
    if len(msg.data.get("entities", [])) == 0:
        return None

    parsed_value = msg.data["entities"][0]["value"]
    if isinstance(parsed_value, dict):
        parsed_value = parsed_value["from"]

    result = datetime.fromisoformat(parsed_value)
    return result.replace(tzinfo=None)


class ValidateDepartureTime(Action):
    def name(self) -> str:
        return "validate_departure_time"

    def run(
            self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> List[EventType]:
        current_value = tracker.get_slot("departure_time")
        if current_value is None:
            return []

        from datetime import datetime as dt
        time_object =  dt.strptime(current_value, "%I %p").time()

        return [SlotSet("departure_time", time_object)]
    

class ActionProvideTransitDetails(Action):
    def name(self) -> Text:
        return "action_provide_transit_details"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
       
        # Get origin and destination slots
        origin = tracker.get_slot("current_location")
        destination = tracker.get_slot("destination_location")
        transit_mode = tracker.get_slot("transit_mode")
        if not transit_mode:
            transit_mode = "bus"
        departure_time = tracker.get_slot("departure_time")
        if not departure_time:
            departure_time = datetime.datetime.now()

        route, _, _, _ = get_transit_route(origin, destination, transit_mode, departure_time)
        return dispatcher.utter_template(template="utter_provide_transit_details", route=route, tracker=tracker)
    
class ActionProvideFareDetails(Action):
    def name(self) -> Text:
        return "action_provide_fare_details"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
       
        fare_from_transit = None
        # Get origin and destination slots
        origin = tracker.get_slot("current_location")
        destination = tracker.get_slot("destination")
        transit_mode = tracker.get_slot("transit_mode")
        departure_time = tracker.get_slot("departure_time")

        _, fare_from_transit, _, _ = get_transit_route(origin, destination, transit_mode, departure_time, get_fare_details=True)
        return dispatcher.utter_template(template="utter_provide_fare_details", fare=fare_from_transit)
    
class ActionProvideArrivalTime(Action):
    def name(self) -> Text:
        return "action_provide_arrival_time"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
       
        # Get origin and destination slots
        origin = tracker.get_slot("current_location")
        destination = tracker.get_slot("destination")
        transit_mode = tracker.get_slot("transit_mode")
        departure_time = tracker.get_slot("departure_time")

        _, _, arrival_time_from_transit, _ = get_transit_route(origin, destination, transit_mode, departure_time, get_arrival_time=True)
        return dispatcher.utter_template(template="utter_provide_arrival_time_details", arrival_time=arrival_time_from_transit)