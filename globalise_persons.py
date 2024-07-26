#!/usr/bin/env python
# coding: utf-8

# <h1>Table of Contents<span class="tocSkip"></span></h1>
# <div class="toc"><ul class="toc-item"></ul></div>

# In[1]:


from datetime import datetime
from typing import List, Optional
import pandas as pd
from tqdm.notebook import tqdm


# In[2]:


def vali_date(date_string: str) -> bool:
    formats = ["%Y", "%Y-%m", "%Y-%m-%d"]
    
    for format_string in formats:
        try:
            datetime.strptime(date_string, format_string)
            return True
        except ValueError:
            if date_string == '-1': #if a date is not known, the only acceptable value is -1
                return True
            else:
                pass
        except TypeError:
            pass
    
    return False


# In[3]:


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


# In[4]:


class Person_attribute:
    def __init__(self, annotation, startdate, enddate, source: str):
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
        


# In[5]:


class Person_attribute_loc(Person_attribute):
    def __init__(self, annotation, startdate, enddate, source, location):
        super().__init__(annotation, startdate, enddate, source)
        if type(location) == str: #needs to be an uri eventually
            self.location = location
        else:
            raise ValueError('Please format the location as as str')


# In[6]:


class Appellation(Person_attribute):
    #has Person_attribute as parent
    def __init__(self, annotation, startdate, enddate, source, app_str, app_type):
        super().__init__(annotation, startdate, enddate, source)
        if type(app_str) == str:
            self.app_str = app_str #the appellation string
        else:
            raise ValueError('Please format your appellation as a string')
        if type(app_type) == str:
            self.app_type = app_type #the appellation type. Can be a str for now, needs to be an URI in the future
        else:
            raise ValueError('Please format your appellation type as a string')
     
        
    def __str__(self) -> str:
        return f"this person was recorded under the {self.app_type} of {self.app_str} in {self.annotation} according to {self.source}"


# In[7]:


class Activity(Person_attribute_loc):
    
    def __init__(self, annotation, startdate, enddate, source, function, function_type, employer, location):
        
        super().__init__(annotation, startdate, enddate, source, location)
        
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
        return f"this person was active as a {self.function} in {self.location}, which is a(n) {self.function_type}, for {self.employer} from {self.startdate} to {self.enddate} as noted in {self.source} on {self.annotation}"


# In[8]:


class Identity(Person_attribute_loc):
    
    def __init__(self, annotation, startdate, enddate, source, identifier, identity_type, location):
        super().__init__(annotation, startdate, enddate, source, location)
        
        if type(identifier) == str: #needs to be URI eventually
            self.identifier = identifier
        else:
            raise ValueError('Please format your identifier as a str')
               
        if type(identity_type) == str: #needs to be URI eventually
            self.identity_type = identity_type
        else:
            raise ValueError('Please format your identity type as a str')    
            
    def __str__(self) -> str:
        return f"this person was identified as {self.identifier}, a {self.identity_type} from {self.startdate} to {self.enddate} in {self.location}, according to {self.source} recorded on {self.annotation}"


# In[9]:


class Status(Person_attribute_loc):
    
    def __init__(self, annotation, startdate, enddate, source, stat, status_type, location):
        super().__init__(annotation, startdate, enddate, source, location)
        
        if type(stat) == str: #needs to be URI eventually
            self.stat = stat
        else:
            raise ValueError('Please format your stat as a str')
               
        if type(status_type) == str: #needs to be URI eventually
            self.status_type = status_type
        else:
            raise ValueError('Please format your status type as a str')
            
    def __str__(self) -> str:
        return f"this person held the status of {self.stat}, a {self.status_type} from {self.startdate} to {self.enddate} in {self.location}, according to {self.source} recorded on {self.annotation}"


# In[10]:


class Location_Relation(Person_attribute_loc):
    
    def __init__(self, annotation, startdate, enddate, source, location_relation, location):
        super().__init__(annotation, startdate, enddate, source, location)
        
        if type(location_relation) == str: #needs to be an uri eventually
            self.location_relation = location_relation
        else:
            raise ValueError('Please format the location to relation as a str')
            
    def __str__(self) -> str:
        return f"this person had a relation of {self.location_relation} to {self.location} from {self.startdate} to {self.enddate}, according to {self.source} recorded on {self.annotation}"


# In[11]:


class Relationship(Person_attribute):
    
    def __init__(self, annotation, startdate, enddate, source, relation, otherPerson):
        super().__init__(annotation, startdate, enddate, source)
        
        if type(relation) == str: #needs to be an uri eventually
            self.relation = relation
        else:
            raise ValueError('Please properly format the relationship as an str')
            
        if type(otherPerson) == str: #needs to be an uri eventually
            self.otherPerson = otherPerson
        else:
            raise ValueError('Please properly format the other person reference as an str')
            
    def __str__(self) -> str:
        return f"this person had a relationship of {self.relation} to {self.otherPerson} from {self.startdate} to {self.enddate}, according to {self.source} recorded on {self.annotation}"


# In[1]:


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
        location_relations: Optional[List[Location_Relation]] = None
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
        
    def printinfo(self):
        print(f"URI: {self.URI}")
        #for p in self.previousURI:
            #print(f"Previous URI: {p}")
        print(f"DOB: {self.DOB}")
        print(f"DOD: {self.DOD}")
        for a in self.appellations:
            print(a)
        print('\n')
        for a in self.active_as:
            print(a)
        print('\n')
        for i in self.identified_as:
            print(i)
        print('\n')
        for s in self.status:
            print(s)
        print('\n')
        for r in self.relationships:
            print(r)
        print('\n')
        for l in self.location_relations:
            print(l)
        
    def __str__(self) -> str:
        return self.URI
    
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


# In[13]:


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
    
    def to_excel(self, makeOverview=True, makeAppellations=True, makeActive_as=True, makeIdentified_as=True, makeStatus=True, makeLocation_relations=True, makeRelationships=True):
        if makeOverview:
            overviewFrame = []
            for p in self.persons:
                overviewFrame.append([p.URI, p.DOB, p.DOD])
            overviewFrame = pd.DataFrame(overviewFrame, columns=['URI', 'DOB', 'DOD'])
        if makeAppellations:
            appellationsFrame = []
            for p in self.persons:
                for a in p.appellations:
                    appellationsFrame.append([p.URI, a.app_str, a.app_type, a.annotation, a.startdate, a.enddate, a.source])
            appellationsFrame = pd.DataFrame(appellationsFrame, columns=['URI','Appellation', 'AppellationType', 'AnnotationDate', 'Startdate', 'Enddate', 'Source'])
        if makeActive_as:
            activeAsFrame = []
            for p in self.persons:
                for a in p.active_as:
                    activeAsFrame.append([p.URI, a.function, a.function_type, a.employer, a.location, a.annotation, a.startdate, a.enddate, a.source])
            activeAsFrame = pd.DataFrame(activeAsFrame, columns=['URI', 'Activity', 'ActivityType', 'Employer', 'Location', 'AnnotationDate', 'StartDate', 'EndDate', 'Source'])
        if makeIdentified_as:
            identifiedAsFrame = []
            for p in self.persons:
                for identity in p.identified_as:
                    identifiedAsFrame.append([p.URI, identity.identifier, identity.identity_type, identity.location, identity.annotation, identity.startdate, identity.enddate, identity.source])
            identifiedAsFrame = pd.DataFrame(identifiedAsFrame, columns=['URI', 'Identity', 'IdentityType', 'Location', 'AnnotationDate', 'StartDate', 'EndDate', 'Source'])
        if makeStatus:
            statusFrame = []
            for p in self.persons:
                for status in p.status:
                    statusFrame.append([p.URI, status.stat, status.status_type, status.location, status.annotation, status.startdate, status.enddate, status.source])
            statusFrame = pd.DataFrame(statusFrame, columns=['URI', 'Status', 'StatusType', 'Location', 'AnnotationDate', 'StartDate', 'EndDate', 'Source'])
        if makeLocation_relations:
            locationRelationFrame = []
            for p in self.persons:
                for lr in p.location_relations:
                    locationRelationFrame.append([p.URI, lr.location_relation, lr.location, lr.annotation, lr.startdate, lr.enddate, lr.source])
            locationRelationFrame = pd.DataFrame(locationRelationFrame, columns=['URI', 'LocationRelation', 'Location', 'AnnotationDate', 'StartDate', 'EndDate', 'Source'])
        if makeRelationships:
            relationFrame = []
            for p in self.persons:
                for r in p.relationships:
                    relationFrame.append([p.URI, r.relation, r.otherPerson, r.annotation, r.startdate, r.enddate, r.source])
            relationFrame = pd.DataFrame(relationFrame, columns=['URI', 'Relation', 'OtherPerson', 'AnnotationDate', 'StartDate', 'EndDate', 'Source'])     
           
        
        return overviewFrame.to_excel('overview.xlsx'), appellationsFrame.to_excel('appellations.xlsx'), activeAsFrame.to_excel('activities.xlsx'), identifiedAsFrame.to_excel('identities.xlsx'), statusFrame.to_excel('status.xlsx'), locationRelationFrame.to_excel('locationRelations.xlsx'), relationFrame.to_excel('relationships.xlsx')
    
    def to_csv(self, makeOverview=True, makeAppellations=True, makeActive_as=True, makeIdentified_as=True, makeStatus=True, makeLocation_relations=True, makeRelationships=True):
        if makeOverview:
            overviewFrame = []
            for p in self.persons:
                overviewFrame.append([p.URI, p.DOB, p.DOD])
            overviewFrame = pd.DataFrame(overviewFrame, columns=['URI', 'DOB', 'DOD'])
        if makeAppellations:
            appellationsFrame = []
            for p in self.persons:
                for a in p.appellations:
                    appellationsFrame.append([p.URI, a.app_str, a.app_type, a.annotation, a.startdate, a.enddate, a.source])
            appellationsFrame = pd.DataFrame(appellationsFrame, columns=['URI','Appellation', 'AppellationType', 'AnnotationDate', 'Startdate', 'Enddate', 'Source'])
        if makeActive_as:
            activeAsFrame = []
            for p in self.persons:
                for a in p.active_as:
                    activeAsFrame.append([p.URI, a.function, a.function_type, a.employer, a.location, a.annotation, a.startdate, a.enddate, a.source])
            activeAsFrame = pd.DataFrame(activeAsFrame, columns=['URI', 'Activity', 'ActivityType', 'Employer', 'Location', 'AnnotationDate', 'StartDate', 'EndDate', 'Source'])
        if makeIdentified_as:
            identifiedAsFrame = []
            for p in self.persons:
                for identity in p.identified_as:
                    identifiedAsFrame.append([p.URI, identity.identifier, identity.identity_type, identity.location, identity.annotation, identity.startdate, identity.enddate, identity.source])
            identifiedAsFrame = pd.DataFrame(identifiedAsFrame, columns=['URI', 'Identity', 'IdentityType', 'Location', 'AnnotationDate', 'StartDate', 'EndDate', 'Source'])
        if makeStatus:
            statusFrame = []
            for p in self.persons:
                for status in p.status:
                    statusFrame.append([p.URI, status.stat, status.status_type, status.location, status.annotation, status.startdate, status.enddate, status.source])
            statusFrame = pd.DataFrame(statusFrame, columns=['URI', 'Status', 'StatusType', 'Location', 'AnnotationDate', 'StartDate', 'EndDate', 'Source'])
        if makeLocation_relations:
            locationRelationFrame = []
            for p in self.persons:
                for lr in p.location_relations:
                    locationRelationFrame.append([p.URI, lr.location_relation, lr.location, lr.annotation, lr.startdate, lr.enddate, lr.source])
            locationRelationFrame = pd.DataFrame(locationRelationFrame, columns=['URI', 'LocationRelation', 'Location', 'AnnotationDate', 'StartDate', 'EndDate', 'Source'])
        if makeRelationships:
            relationFrame = []
            for p in self.persons:
                for r in p.relationships:
                    relationFrame.append([p.URI, r.relation, r.otherPerson, r.annotation, r.startdate, r.enddate, r.source])
            relationFrame = pd.DataFrame(relationFrame, columns=['URI', 'Relation', 'OtherPerson', 'AnnotationDate', 'StartDate', 'EndDate', 'Source'])     
           
        
        return overviewFrame.to_csv('overview.csv'), appellationsFrame.to_csv('appellations.csv'), activeAsFrame.to_csv('activities.csv'), identifiedAsFrame.to_csv('identities.csv'), statusFrame.to_csv('status.csv'), locationRelationFrame.to_csv('locationRelations.csv'), relationFrame.to_csv('relationships.csv')


# In[ ]:




