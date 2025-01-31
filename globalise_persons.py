#!/usr/bin/env python
# coding: utf-8

# In[1]:


from datetime import datetime
from typing import List, Optional
import pandas as pd
from tqdm.notebook import tqdm


from sqlalchemy.exc import OperationalError
from sqlalchemy import * 
from sqlalchemy.orm import *

import re

import csv

import copy


# In[2]:


uri_identifier = 'https://digitaalerfgoed.poolparty.biz/globalise/'


# In[ ]:





# In[3]:


atomize_list = [' en ', ',', 'mitsgaders', ';', 'EN', ', en']

def load_tuples(split_file, nosplit_file):
    with open(split_file, 'r') as f:
        split_tuple = tuple(line.strip() for line in f.readlines())
    with open(nosplit_file, 'r') as f:
        nosplit_tuple = tuple(line.strip() for line in f.readlines())
    return split_tuple, nosplit_tuple

def save_tuples(split_tuple, nosplit_tuple, split_file, nosplit_file):
    with open(split_file, 'w') as f:
        for item in split_tuple:
            f.write(f"{item}\n")
    with open(nosplit_file, 'w') as f:
        for item in nosplit_tuple:
            f.write(f"{item}\n")


# In[4]:


def vali_date(date_string: str) -> bool:
    if date_string == '-1':  # If a date is not known, the only acceptable value is -1
        return True

    formats = ["%Y", "%Y-%m", "%Y-%m-%d"]
    
    for format_string in formats:
        try:
            datetime.strptime(date_string, format_string)
            return True
        except ValueError:
            continue  # Try the next format
        except TypeError:
            return False  # date_string is not a string
    
    return False


# In[5]:


def combine_lists(x: list, y: list) -> list:
    # Check if both x and y are non-empty lists
    if x and y:
        z = x + y
        return z
    elif x:
        return x
    elif y:
        return y
    else:
        # Return an empty list if both x and y are empty
        return []


# In[6]:


class Person_attribute:
    def __init__(self, annotation, startdate, enddate, source: str, page: str, observation_id: str, original_label: str):
        if vali_date(annotation):
            self.annotation = annotation #date
        else:
            raise ValueError('Only a valid date following the ISO 8601 standard can be used. It can be yyyy, yyyy-mm, or yyyy-mm-dd')
        if vali_date(startdate):
            self.startdate = startdate #date
        else:
            raise ValueError('Only a valid date following the ISO 8601 standard can be used. It can be yyyy, yyyy-mm, or yyyy-mm-dd')
        if vali_date(enddate):
            self.enddate = enddate #date
        else:
            raise ValueError('Only a valid date following the ISO 8601 standard can be used. It can be yyyy, yyyy-mm, or yyyy-mm-dd')
        if type(source) == str:
            self.source = source #string
        else:
            raise ValueError('Please format your source as a string')
            
        if type(page) == str:
            self.page = page
        else:
            raise ValueError('Please format your page as a string')
            
        if type(observation_id) == str:
            self.observation_id = observation_id
        else:
            raise ValueError('Please format your observation_id as a string')
            
        if type(original_label) == str:
            self.original_label = original_label
        else:
            raise ValueError('Please format your original label as a string')
            
    def split_up_string(self, input_string, exceptions=False):
        if exceptions:
            if type(exceptions) is set:
                if input_string in exceptions:
                    output = []
                    output.append(input_string)
                    return output
                else:
                    escaped_substrings = [re.escape(substring) for substring in atomize_list]
                    pattern = '|'.join(escaped_substrings)
                    split_result = re.split(pattern, input_string)
                    split_result = [substring.strip() for substring in split_result]
                
            else:
                raise TypeError('exceptions should be formatted as a set')
        else:    
            escaped_substrings = [re.escape(substring) for substring in atomize_list]
            pattern = '|'.join(escaped_substrings)
            split_result = re.split(pattern, input_string)
            split_result = [substring.strip() for substring in split_result]
    
        return split_result
        


# In[7]:


class Person_attribute_loc(Person_attribute):
    def __init__(self, annotation, startdate, enddate, source, page, observation_id, original_label, location):
        super().__init__(annotation, startdate, enddate, source, page, observation_id, original_label)
        self.location = location            


# In[8]:


class Appellation(Person_attribute_loc):
    #has Person_attribute as parent
    def __init__(self, annotation, startdate, enddate, source, page, observation_id, app_str, app_type, location):
        super().__init__(annotation, startdate, enddate, source, page, observation_id, '-1', location)
        if type(app_str) == str:
            self.app_str = app_str #the appellation string
        else:
            raise ValueError('Please format your appellation as a string')
        if type(app_type) == str:
            self.app_type = app_type #the appellation type. Can be a str for now, needs to be an URI in the future
        else:
            raise ValueError('Please format your appellation type as a string')
     
        
    def __str__(self) -> str:
        return f"this person was recorded under the {self.app_type} of {self.app_str} according to {self.source} recorded at the following point in time: {self.annotation}"


# In[9]:


class Event(Person_attribute_loc):
    
    def __init__(self, annotation, startdate, enddate, source, page, observation_id, original_label, event, argument, location):
        super().__init__(annotation, startdate, enddate, source, page, observation_id, original_label, location)
        
        if type(event) == str: #needs to be URI eventually
            self.event = event
        else:
            raise ValueError('Please format your event as a str')
               
        if type(argument) == str: #needs to be URI eventually
            self.argument = argument
        else:
            raise ValueError('Please format your identity type as a str')    
            
    def __str__(self) -> str:
        return f"this person was identified as {self.argument} in a {self.event} event from {self.startdate} to {self.enddate} in {self.location}, according to {self.source} recorded at the following point in time: {self.annotation}"


# In[10]:


class Activity(Person_attribute_loc):
    
    def __init__(self, annotation, startdate, enddate, source, page, observation_id, original_label, function, function_type, employer, location):
        
        super().__init__(annotation, startdate, enddate, source, page, observation_id, original_label, location)
        
        if type(function) == str: #needs to be an uri eventually
            self.function = function
        else:
            raise ValueError('Please format the function as a str')
        if type(function_type) == str: #needs to be an uri eventually
            self.function_type = function_type
        else:
            raise ValueError('Please format the function type as a str')
        if type(employer) == str: #needs to be an uri eventually
            self.employer = employer
        else:
            raise ValueError('Please format the employer as a str')
            
    def __str__(self) -> str:
        return f"According to observation {self.observation_id} this person was active as a {self.original_label}, disambiguated as {self.function} in {self.location}, which is a(n) {self.function_type}. They were employed by {self.employer} from {self.startdate} to {self.enddate} as noted in {self.source} recorded at the following point in time: {self.annotation}"
    
    def atomize(self, atomize_exceptions=False, dont_process_list=False):
        if atomize_exceptions:
            split = super().split_up_string(self.function, exceptions=atomize_exceptions)
        else:
            split = super().split_up_string(self.function)
        if len(split) > 1:
            output = []
            for x in split:
                output.append(Activity(self.annotation, 
                                       self.startdate, 
                                       self.enddate, 
                                       self.source, 
                                       self.page, 
                                       self.observation_id, 
                                       self.original_label, 
                                       x,
                                       self.function_type, 
                                       self.employer, 
                                       self.location))
            return output
        
    def atomize_location(self, atomize_exceptions=False):
        if atomize_exceptions:
            split = super().split_up_string(self.location, exceptions=atomize_exceptions)
        else:
            split = super().split_up_string(self.location)
        if len(split) > 1:
            output = []
            for x in split:
                output.append(Activity(self.annotation, 
                                       self.startdate, 
                                       self.enddate, 
                                       self.source, 
                                       self.page, 
                                       self.observation_id, 
                                       self.original_label, 
                                       self.function, 
                                       self.function_type, 
                                       self.employer, 
                                       x))
            return output


# In[11]:


class Identity(Person_attribute_loc):
    
    def __init__(self, annotation, startdate, enddate, source, page, observation_id, original_label, identifier, identity_type, location):
        super().__init__(annotation, startdate, enddate, source, page, observation_id, original_label, location)
        
        if type(identifier) == str: #needs to be URI eventually
            self.identifier = identifier
        else:
            raise ValueError('Please format your identifier as a str')
               
        if type(identity_type) == str: #needs to be URI eventually
            self.identity_type = identity_type
        else:
            raise ValueError('Please format your identity type as a str')    
            
    def __str__(self) -> str:
        return f"this person was identified as {self.original_label}, GLOBALISE identity type: {self.identity_type} from {self.startdate} to {self.enddate} in {self.location}, according to {self.source} recorded at the following point in time: {self.annotation}"


# In[12]:


class Status(Person_attribute_loc):
    
    def __init__(self, annotation, startdate, enddate, source, page, observation_id, original_label, stat, status_type, location):
        super().__init__(annotation, startdate, enddate, source, page, observation_id, original_label, location)
        
        if type(stat) == str: #needs to be URI eventually
            self.stat = stat
        else:
            raise ValueError('Please format your stat as a str')
               
        if type(status_type) == str: #needs to be URI eventually
            self.status_type = status_type
        else:
            raise ValueError('Please format your status type as a str')
            
    def __str__(self) -> str:
        return f"this person held the status of {self.stat}, a {self.status_type} from {self.startdate} to {self.enddate} in {self.location}, according to {self.source} recorded at the following point in time: {self.annotation}"


# In[13]:


class Location_Relation(Person_attribute_loc):
    
    def __init__(self, annotation, startdate, enddate, source, page, observation_id, original_label, location_relation, location):
        super().__init__(annotation, startdate, enddate, source, page, observation_id, original_label, location)
        
        if type(location_relation) == str: #needs to be an uri eventually
            self.location_relation = location_relation
        else:
            raise ValueError('Please format the location to relation as a str')
            
    def __str__(self) -> str:
        return f"this person had a relation of {self.location_relation} to {self.location} from {self.startdate} to {self.enddate}, according to {self.source} recorded at the following point in time: {self.annotation}"


# In[14]:


class Relationship(Person_attribute):
    
    def __init__(self, annotation, startdate, enddate, source, page, observation_id, original_label, relation, otherPerson):
        super().__init__(annotation, startdate, enddate, source, page, observation_id, original_label,)
        
        if type(relation) == str: #needs to be an uri eventually
            self.relation = relation
        else:
            raise ValueError('Please properly format the relationship as an str')
            
        if type(otherPerson) == str: #needs to be an uri eventually
            self.otherPerson = otherPerson
        else:
            raise ValueError('Please properly format the other person reference as an str')
            
    def __str__(self) -> str:
        return f"this person had a relationship of {self.original_label} to {self.otherPerson} from {self.startdate} to {self.enddate}, according to {self.source} recorded at the following point in time: {self.annotation}"


# In[31]:


class Person:
    def __init__(
        self,
        URI: str,
        DOB: str,
        DOD: str,
        appellations: Optional[List[Appellation]] = None,
        active_as: Optional[List[Activity]] = None,
        identified_as: Optional[List[Identity]] = None,
        status: Optional[List[Status]] = None,
        relationships: Optional[List[Relationship]] = None,
        location_relations: Optional[List[Location_Relation]] = None,
        events: Optional[List[Event]] = None
    ):
        if not isinstance(URI, str):
            raise TypeError("URI must be a string.")
        self.URI = URI

        if not isinstance(DOB, str):  # Assuming DOB and DOD are stored as strings.
            raise TypeError("DOB must be a string.")
        self.DOB = DOB

        if not isinstance(DOD, str):
            raise TypeError("DOD must be a string.")
        self.DOD = DOD

        # Check that appellations is a list of Appellation objects
        if appellations is not None and not all(isinstance(a, Appellation) for a in appellations):
            raise TypeError("appellations must be a list of Appellation objects.")
        self.appellations = appellations or []

        # Check that active_as is a list of Activity objects
        if active_as is not None and not all(isinstance(a, Activity) for a in active_as):
            raise TypeError("active_as must be a list of Activity objects.")
        self.active_as = active_as or []

        # Check that identified_as is a list of Identity objects
        if identified_as is not None and not all(isinstance(i, Identity) for i in identified_as):
            raise TypeError("identified_as must be a list of Identity objects.")
        self.identified_as = identified_as or []

        # Check that status is a list of Status objects
        if status is not None and not all(isinstance(s, Status) for s in status):
            raise TypeError("status must be a list of Status objects.")
        self.status = status or []

        # Check that relationships is a list of Relationship objects
        if relationships is not None and not all(isinstance(r, Relationship) for r in relationships):
            raise TypeError("relationships must be a list of Relationship objects.")
        self.relationships = relationships or []

        # Check that location_relations is a list of Location_Relation objects
        if location_relations is not None and not all(isinstance(l, Location_Relation) for l in location_relations):
            raise TypeError("location_relations must be a list of Location_Relation objects.")
        self.location_relations = location_relations or []
        
        # Check that location_relations is a list of Location_Relation objects
        if events is not None and not all(isinstance(e, Event) for e in events):
            raise TypeError("events must be a list of Event objects.")
        self.events = events or []
        
    def printinfo(self):
        print(f"URI: {self.URI}")
        #for p in self.previousURI:
            #print(f"Previous URI: {p}")
        #print(f"DOB: {self.DOB}")
        #print(f"DOD: {self.DOD}")
        for a in self.appellations:
            print(a)
        #print('\n')
        for a in self.active_as:
            print(a)
        #print('\n')
        for i in self.identified_as:
            print(i)
        #print('\n')
        for s in self.status:
            print(s)
        #print('\n')
        for r in self.relationships:
            print(r)
        #print('\n')
        for l in self.location_relations:
            print(l)
        for e in self.events:
            print(e)
            
        print("")
        
    def __str__(self) -> str:
        return self.URI
    
    def filter_activities(self, dont_process: List[str]):
        """
        Removes activities from the `active_as` list where the activity's function
        is in the `dont_process` list.

        :param dont_process: List of functions to be excluded.
        """
        dont_process_lower = [function.lower() for function in dont_process]  # Normalize dont_process to lowercase

        if len(self.active_as) < 1:
            return  # No activities to filter

        # Use a filtered list instead of modifying the list in place
        new_active_as = []
        for act in self.active_as:
            if act.function.lower() in dont_process_lower:
                print(f'removed {act.function} from {self.URI}')
            else:
                new_active_as.append(act)

        # Replace the original list with the filtered list
        self.active_as = new_active_as

    
    def add_relationship(self, other, relationsh, inverse_relationship, personlist, annotation, start, end, source, newPerson = True):
        personAuri = self.URI
        if newPerson == True:
            #other should be an appellation of the other person
            personBuri = str(self.URI + 'rela' + other) #generate an URI for the new person
            
            
            #add the relationship to self
            newRelation = Relationship(annotation, start, end, source, relationsh, personBuri) 
            self.relationships.append(newRelation)
            
            #now actually create a person with that uri in the personlist specified
            personB = Person(personBuri,
                            '-1',
                            '-1',
                            [Appellation(annotation, start, end, source, other, 'Appellation')],
                            None,
                            None,
                            None,
                            [Relationship(annotation, start, end, source, inverse_relationship, personAuri)])
            personlist.persons.append(personB)
        else:
            newRelation = Relationship (annotation, start, end, source, relationsh, other)
            self.relationships.append(newRelation)
            
            #something to do the inverse?
            personB = Person(other,
                            '-1',
                            '-1',
                            None,
                            None,
                            None,
                            None,
                            [Relationship(annotation, start, end, source, inverse_relationship, personAuri)])
            personlist.persons.append(personB)
            #is het logischer om dit op lijstniveau te doen?
            #requires you call a merge action on the whole list later
            #print("do not forget to call a merge_on_uri on your personlist later!")
           
    def __add__(self, other):
        if isinstance(other, Person):
            #newURI = self.URI + other.URI
            #we'll assume the DOB and DOD are compatible by default, for now
            newappellations = combine_lists(self.appellations, other.appellations)
            newactivities = combine_lists(self.active_as, other.active_as)
            newidentities = combine_lists(self.identified_as, other.identified_as)
            newstatus = combine_lists(self.status, other.status)
            newrelations = combine_lists(self.relationships, other.relationships)
            newlocationrelations = combine_lists(self.location_relations, other.location_relations)
            
            return Person(self.URI, self.DOB, self.DOD, newappellations, newactivities, newidentities, newstatus, newrelations, newlocationrelations)
            
        else:
            raise TypeError('Unsupported operand type for +')
            
    def atomize_functions(self, a_exceptions=False):
        if not self.active_as:
            #print(f'There is no active as for this person {self.URI}.')
            pass
            

        new_active_as = []  # Store new activities separately
        for act in self.active_as:
            x = act.atomize(atomize_exceptions=a_exceptions) if a_exceptions else act.atomize()
            if x:
                new_active_as.extend(x)  # Add the split activities
            else:
                new_active_as.append(act)  # Keep the original if not split

        self.active_as = new_active_as  # Replace the list after iteration

     
    def link_functions(self, functions_dict, dont_process=[], error_log_filename='keyerror_log.csv', final_linking=False):
        
        def clean_text(text: str) -> str:
            text = text.lower().strip()
            text = re.sub(r'\s+', ' ', text)
            text = text.replace(',', '')
            return text

        def create_new_activity(original_activity, new_function_value):
            new_activity = copy.deepcopy(original_activity)
            new_activity.function = new_function_value
            return new_activity

        new_active_as = []


        clean_dont_process = []
        for item in dont_process:
            clean_dont_process.append(clean_text(item))
        clean_dont_process = set(clean_dont_process)


        # Open the CSV file for appending the error log
        with open(error_log_filename, mode='a', newline='') as csvfile:
            error_writer = csv.writer(csvfile)

            # Process the active_as list
            for a in self.active_as:
                x = clean_text(a.function)
                #print(x)

                if x in clean_dont_process:
                    #print(f"removing {x} from {self.URI}")
                    pass
                else:
                    try:
                        # Try to replace the function
                        disambiguated_uri = functions_dict[x]
                        new_active_as.append(create_new_activity(a, disambiguated_uri))
                        #print(f"replaced with {a.function}")
                        #print("")
                    except KeyError:
                        if final_linking:
                            if a.function.startswith('https://digitaalerfgoed.poolparty.biz/globalise/'):
                                new_active_as.append(create_new_activity(a, a.function))

                            else:
                                # If a KeyError occurs, log it to the CSV file
                                error_writer.writerow([a.function])  # Write the problematic function to a new row
                                new_active_as.append(create_new_activity(a, '-1'))
                        else:
                            new_active_as.append(create_new_activity(a, a.function))

        self.active_as = new_active_as  # Replace the list after iteration
                    
    def atomize_function_locations(self, a_exceptions=False):
        if len(self.active_as) < 1:
            print('There is no active as for this person.')
        else:
            if a_exceptions:
                for act in self.active_as:
                    x = act.atomize_location(atomize_exceptions=a_exceptions)
                    if x:
                        for y in x:
                            self.active_as.append(y)
                        self.active_as.remove(act)
                        
            else:
                for act in self.active_as:
                    x = act.atomize_location()
                    if x:
                        for y in x:
                            self.active_as.append(y)
                        self.active_as.remove(act)


# In[16]:


class Personlist:
    def __init__(self, persons: [List[Person]]):
        # Check that persons is a list of Person objects
        if not all(isinstance(a, Person) for a in persons):
            raise TypeError("This object must consist of a list of Person objects")
        self.persons = persons
        
    def __str__(self) -> str:
        x = len(self.persons)
        return f"a list containing {x} persons"
    
    def merge_lists(self, list1, list2):
        # Helper function to merge two lists and remove duplicates
        unique_items = set(list1) | set(list2)
        return list(unique_items)
    
    def atomize_functions_list(self, use_exceptions=False):
        for p in self.persons:
            if use_exceptions:
                p.atomize_functions(a_exceptions=use_exceptions)
            else:
                p.atomize_functions()
    
    def filter_activities_for_all(self, non_allowed_activities: List[str]):
        """
        Applies the filter_activities method for each person in the list.
        :param allowed_activities: List of allowed activities to keep.
        """
        for p in self.persons:
            p.filter_activities(non_allowed_activities)
    
    def print_all_persons(self):
        for p in self.persons:
            p.printinfo()
    
    def link_functions_list(self, functions_dict, dont_process=[], final_linking_round=False):
        for p in self.persons:
            p.link_functions(functions_dict, dont_process, final_linking=final_linking_round)
            
    def atomize_function_locations_list(self, use_exceptions=False):
        for p in self.persons:
            if use_exceptions:
                p.atomize_function_locations(a_exceptions=use_exceptions)
            else:
                p.atomize_function_locations()

    def merge_on_uri(self) -> List[Person]:
        output = []
        for p in self.persons:
            found = False
            for c in output:
                if c.URI == p.URI:
                    # Merge appellations without duplicates
                    c.appellations = self.merge_lists(c.appellations, p.appellations)
                    # Merge activities without duplicates
                    c.active_as = self.merge_lists(c.active_as, p.active_as)
                    # Merge identities without duplicates
                    c.identified_as = self.merge_lists(c.identified_as, p.identified_as)
                    # Merge statuses without duplicates
                    c.status = self.merge_lists(c.status, p.status)
                    # Merge relationships without duplicates
                    c.relationships = self.merge_lists(c.relationships, p.relationships)
                    # Merge location_relations without duplicates
                    c.location_relations = self.merge_lists(c.location_relations, p.location_relations)
                    found = True
                    break
            if not found:
                output.append(p)
        return output             
    
    def to_csv(self, makeOverview=True, makeAppellations=True, makeActive_as=True, makeIdentified_as=True, makeStatus=True, makeLocation_relations=True, makeRelationships=True, makeEvents=True):
        if makeOverview:
            overviewFrame = []
            for p in self.persons:
                overviewFrame.append([p.URI, p.DOB, p.DOD])
            overviewFrame = pd.DataFrame(overviewFrame, columns=['URI', 'DOB', 'DOD'])
        if makeAppellations:
            appellationsFrame = []
            for p in self.persons:
                for a in p.appellations:
                    appellationsFrame.append([p.URI, a.observation_id, a.app_str, a.app_type, a.annotation, a.startdate, a.enddate, a.location, a.source, a.page])
            appellationsFrame = pd.DataFrame(appellationsFrame, columns=['URI', 'Observation', 'Appellation', 'AppellationType', 'AnnotationDate', 'Startdate', 'Enddate', 'Location', 'Source', 'Location in Source'])
        if makeActive_as:
            activeAsFrame = []
            for p in self.persons:
                for a in p.active_as:
                    activeAsFrame.append([p.URI, a.observation_id, a.original_label, a.function, a.function_type, a.employer, a.location, a.annotation, a.startdate, a.enddate, a.source, a.page])
            activeAsFrame = pd.DataFrame(activeAsFrame, columns=['URI', 'Observation', 'Original Label', 'Activity', 'ActivityType', 'Employer', 'Location', 'AnnotationDate', 'StartDate', 'EndDate', 'Source', 'Location in Source'])
        if makeIdentified_as:
            identifiedAsFrame = []
            for p in self.persons:
                for identity in p.identified_as:
                    identifiedAsFrame.append([p.URI, identity.observation_id, identity.original_label, identity.identifier, identity.identity_type, identity.location, identity.annotation, identity.startdate, identity.enddate, identity.source, identity.page])
            identifiedAsFrame = pd.DataFrame(identifiedAsFrame, columns=['URI', 'Observation', 'Original Label', 'Identity', 'IdentityType', 'Location', 'AnnotationDate', 'StartDate', 'EndDate', 'Source', 'Location in Source'])
        if makeStatus:
            statusFrame = []
            for p in self.persons:
                for status in p.status:
                    statusFrame.append([p.URI, status.observation_id, status.original_label, status.stat, status.status_type, status.location, status.annotation, status.startdate, status.enddate, status.source, status.page])
            statusFrame = pd.DataFrame(statusFrame, columns=['URI', 'Observation', 'Original Label', 'Status', 'StatusType', 'Location', 'AnnotationDate', 'StartDate', 'EndDate', 'Source', 'Location in Source'])
        if makeLocation_relations:
            locationRelationFrame = []
            for p in self.persons:
                for lr in p.location_relations:
                    locationRelationFrame.append([p.URI, lr.observation_id, lr.original_label, lr.location_relation, lr.location, lr.annotation, lr.startdate, lr.enddate, lr.source, lr.page])
            locationRelationFrame = pd.DataFrame(locationRelationFrame, columns=['URI', 'Observation', 'Original Label', 'LocationRelation', 'Location', 'AnnotationDate', 'StartDate', 'EndDate', 'Source', 'Location in Source'])
        if makeRelationships:
            relationFrame = []
            for p in self.persons:
                for r in p.relationships:
                    relationFrame.append([p.URI, r.observation_id, r.original_label, r.relation,  r.otherPerson, r.annotation, r.startdate, r.enddate, r.source, r.page])
            relationFrame = pd.DataFrame(relationFrame, columns=['URI', 'Observation', 'Original Label','Relation', 'OtherPerson', 'AnnotationDate', 'StartDate', 'EndDate', 'Source', 'Location in Source'])     
        
        if makeEvents:
            eventsFrame = []
            for p in self.persons:
                for e in p.events:
                    eventsFrame.append([p.URI, e.observation_id, e.original_label, e.event, e.argument, e.location, e.annotation, e.startdate, e.enddate, e.source, e.page])
            eventsFrame = pd.DataFrame(eventsFrame, columns=['URI', 'Observation', 'Original Label', 'Event', 'Argument', 'Location', 'AnnotationDate', 'StartDate', 'EndDate', 'Source', 'Location in Source'])
        
        return overviewFrame.to_csv('overview.csv'), appellationsFrame.to_csv('appellations.csv'), activeAsFrame.to_csv('activities.csv'), identifiedAsFrame.to_csv('identities.csv'), statusFrame.to_csv('status.csv'), locationRelationFrame.to_csv('locationRelations.csv'), relationFrame.to_csv('relationships.csv'), eventsFrame.to_csv('events.csv')
    
    def update_db(self, db, makeOverview=True, makeAppellations=True, makeActive_as=True, makeIdentified_as=True, makeStatus=True, makeLocation_relations=True, makeRelationships=True, makeEvents=True):
    
        #create engine
        engine = create_engine(f'sqlite:///{db}')
        metadata = MetaData(f'sqlite:///{db}')

        #copy the .schema into the metadata
        metadata.reflect(bind=engine)

        #create a session with autoflush off
        Session = sessionmaker(bind=engine, autoflush=False)
        session = Session()

        #for each table, check if it needs to be constructed
        if makeOverview:
            #if so, connect the table to a variable
            overview_table = metadata.tables['persons']

            #create an empty object to bind to the table
            class Overview_sql(object): pass

            #map table to object
            mapper(Overview_sql, overview_table)

            for p in tqdm(self.persons):
                new_overview_sql = Overview_sql()
                new_overview_sql.URI = p.URI
                session.merge(new_overview_sql)

        if makeAppellations:
            #if so, connect the table to a variable
            appellation_table = metadata.tables['appellations']

            #create an empty object to bind to the table
            class Appellation_sql(object): pass

            #map table to object
            mapper(Appellation_sql, appellation_table)

            for p in tqdm(self.persons):
                for a in p.appellations:
                    new_appellation_sql = Appellation_sql()
                    new_appellation_sql.URI = p.URI
                    new_appellation_sql.observation_id = a.observation_id
                    new_appellation_sql.appellation = a.app_str
                    new_appellation_sql.appellationType = a.app_type 
                    new_appellation_sql.annotationDate = a.annotation
                    new_appellation_sql.startDate = a.startdate
                    new_appellation_sql.endDate = a.enddate
                    new_appellation_sql.location = a.location
                    new_appellation_sql.source = a.source
                    new_appellation_sql.location_in_source = a.page

                    session.merge(new_appellation_sql)
                    

        if makeActive_as:
            #if so, connect the table to a variable
            activeAs_table = metadata.tables['activeAs']

            #create an empty object to bind to the table
            class activeAs_sql(object): pass

            #map table to object
            mapper(activeAs_sql, activeAs_table)

            for p in tqdm(self.persons):
                for a in p.active_as:
                    new_activeAs_sql = activeAs_sql()
                    new_activeAs_sql.URI = p.URI
                    new_activeAs_sql.observation_id = a.observation_id
                    new_activeAs_sql.original_label = a.original_label
                    new_activeAs_sql.activity = a.function
                    new_activeAs_sql.activityType = a.function_type 
                    new_activeAs_sql.employer = a.employer
                    new_activeAs_sql.annotationDate = a.annotation
                    new_activeAs_sql.startDate = a.startdate
                    new_activeAs_sql.endDate = a.enddate
                    new_activeAs_sql.location = a.location
                    new_activeAs_sql.source = a.source
                    new_activeAs_sql.location_in_source = a.page

                    session.merge(new_activeAs_sql)
                    


        if makeIdentified_as:
            #if so, connect the table to a variable
            identities_table = metadata.tables['identities']

            #create an empty object to bind to the table
            class Identity_sql(object): pass

            #map table to object
            mapper(Identity_sql, identities_table)

            for p in tqdm(self.persons):
                for a in p.identified_as:
                    new_Identity_sql = Identity_sql()
                    new_Identity_sql.URI = p.URI
                    new_Identity_sql.observation_id = a.observation_id
                    new_Identity_sql.original_label = a.original_label
                    new_Identity_sql.identity = a.identifier
                    new_Identity_sql.identityType = a.identity_type 
                    new_Identity_sql.annotationDate = a.annotation
                    new_Identity_sql.startDate = a.startdate
                    new_Identity_sql.endDate = a.enddate
                    new_Identity_sql.location = a.location
                    new_Identity_sql.source = a.source
                    new_Identity_sql.location_in_source = a.page

                    session.merge(new_Identity_sql)

        if makeStatus:
            #if so, connect the table to a variable
            statuses_table = metadata.tables['statuses']

            #create an empty object to bind to the table
            class Status_sql(object): pass

            #map table to object
            mapper(Status_sql, statuses_table)

            for p in tqdm(self.persons):
                for a in p.status:
                    new_Status_sql = Status_sql()
                    new_Status_sql.URI = p.URI
                    new_Status_sql.observation_id = a.observation_id
                    new_Status_sql.original_label = a.original_label
                    new_Status_sql.status = a.stat
                    new_Status_sql.statusType = a.status_type 
                    new_Status_sql.annotationDate = a.annotation
                    new_Status_sql.startDate = a.startdate
                    new_Status_sql.endDate = a.enddate
                    new_Status_sql.location = a.location
                    new_Status_sql.source = a.source
                    new_Status_sql.location_in_source = a.page

                    session.merge(new_Status_sql)      


        if makeLocation_relations:
            #if so, connect the table to a variable
            locationRelations_table = metadata.tables['locationRelations']

            #create an empty object to bind to the table
            class locationRelation_sql(object): pass

            #map table to object
            mapper(locationRelation_sql, locationRelations_table)

            for p in tqdm(self.persons):
                for a in p.location_relations:
                    new_locationRelation_sql = locationRelation_sql()
                    new_locationRelation_sql.URI = p.URI
                    new_locationRelation_sql.observation_id = a.observation_id
                    new_locationRelation_sql.original_label = a.original_label
                    new_locationRelation_sql.status = a.stat
                    new_locationRelation_sql.statusType = a.status_type 
                    new_locationRelation_sql.annotationDate = a.annotation
                    new_locationRelation_sql.startDate = a.startdate
                    new_locationRelation_sql.endDate = a.enddate
                    new_locationRelation_sql.location = a.location
                    new_locationRelation_sql.source = a.source
                    new_locationRelation_sql.location_in_source = a.page

                    session.merge(new_locationRelation_sql)   


        if makeRelationships:
            #if so, connect the table to a variable
            relations_table = metadata.tables['relations']

            #create an empty object to bind to the table
            class relation_sql(object): pass

            #map table to object
            mapper(relation_sql, relations_table)

            for p in tqdm(self.persons):
                for a in p.relationships:
                    new_relation_sql = relation_sql()
                    new_relation_sql.person = p.URI
                    new_relation_sql.observation_id = a.observation_id
                    new_relation_sql.original_label = a.original_label
                    new_relation_sql.otherPerson = a.otherPerson
                    new_relation_sql.relation = a.relation
                    new_relation_sql.annotationDate = a.annotation
                    new_relation_sql.startDate = a.startdate
                    new_relation_sql.endDate = a.enddate
                    new_relation_sql.source = a.source
                    new_relation_sql.location_in_source = a.page

                    session.merge(new_relation_sql)   
                    
        if makeEvents:
            events_table = metadata.tables['events']
            
            class event_sql(object): pass
            
            #map table to object
            mapper(event_sql, events_table)
            
            for p in tqdm(self.persons):
                for a in p.events:
                    new_event_sql = event_sql()
                    new_event_sql.person = p.URI
                    new_event_sql.observation_id = a.observation_id
                    new_event_sql.original_label = a.original_label
                    new_event_sql.event = a.event
                    new_event_sql.argument = a.argument
                    new_event_sql.annotationDate = a.annotation
                    new_event_sql.startDate = a.startdate
                    new_event_sql.endDate = a.enddate
                    new_event_sql.source = a.source
                    new_event_sql.location_in_source = a.page

                    session.merge(new_event_sql)   

        #after all that

        # Commit the session after all merges are done
        try:
            session.commit()
        except OperationalError as e:
            session.rollback()  # Roll back the transaction on error
            print(f"An error occurred: {e}")    


        session.flush()


# In[17]:


def import_linking_list(filename):
    #Reads a CSV file and converts it into a dictionary where the 'original_label' is the key and the 'URI' is the value.
    result = {}

    # Read the CSV into a DataFrame
    df = pd.read_csv(filename)
    # Convert the DataFrame into a dictionary
    result = dict(zip(df['original_label'].str.strip().str.lower(), df['URI']))

    return result


# In[ ]:




