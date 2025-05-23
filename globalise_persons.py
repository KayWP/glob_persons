#!/usr/bin/env python
# coding: utf-8

# In[1]:


# Standard library imports
from dataclasses import dataclass, field, fields
from typing import Optional, List
import copy
from datetime import datetime  # For vali_date method

# Third-party dependencies
import pandas as pd  # For to_csv method
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import mapper, sessionmaker
from sqlalchemy.exc import OperationalError
from tqdm import tqdm  # For progress bar in update_db method


# In[2]:


@dataclass
class PersonAttribute:
    """Base class for observation-related entities."""
    id: Optional[int] = None
    observation_id: Optional[str] = None
    reconstruction_id: Optional[str] = None
    original_label: Optional[str] = None
    annotationDate: Optional[str] = None
    startDate: Optional[str] = None
    endDate: Optional[str] = None
    startDate_min: Optional[str] = None
    startDate_max: Optional[str] = None
    endDate_min: Optional[str] = None
    endDate_max: Optional[str] = None
    observation_source: Optional[str] = None
    location_in_observation_source: Optional[str] = None
    reconstruction_source: Optional[str] = None
    location_in_reconstruction_source: Optional[str] = None
    comment: Optional[str] = None
        
    def __post_init__(self):
        # First, lowercase all string fields except original_label
        self._lowercase_string_fields()
        
        #validate dates after initialization
        date_fields = [
            "annotationDate", "startDate", "endDate", "startDate_min", "startDate_max", "endDate_min", "endDate_max"            
        ]
        
        for field_name in date_fields:
            date_value = getattr(self, field_name)
            
            if date_value == '-1':
                setattr(self, field_name, None)
            elif date_value is not None and not self.vali_date(date_value):
                raise ValueError(
                    f'Field {field_name} with value "{date_value}" is invalid. '
                    'Only a valid date following the ISO 8601 standard can be used. '
                    'It can be yyyy, yyyy-mm, or yyyy-mm-dd, or -1 for unknown dates.'
                )
    
    def _lowercase_string_fields(self):
        """Convert all string field values to lowercase except original_label."""
        # Get all fields for this instance's class
        class_fields = fields(self)
        
        # Process each field
        for field in class_fields:
            value = getattr(self, field.name)
            
            # Skip None values and original_label field
            if value is None or field.name == 'original_label':
                continue
                
            # Convert string values to lowercase
            if isinstance(value, str) and value:
                setattr(self, field.name, value.lower())
    
    @staticmethod
    def vali_date(date_string: str) -> bool:
        """
        Validates if a string is a proper date format.
        Accepts:
        - ISO 8601 format: yyyy, yyyy-mm, or yyyy-mm-dd
        
        Args:
            date_string: The string to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
            
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


# In[3]:


@dataclass
class PersonAttributeLocation(PersonAttribute):
    """Adds location based methods to PersonAttribute"""
    location: Optional[str] = None


# In[4]:


@dataclass
class Appellation(PersonAttribute):
    """Represents an appellation associated with a person."""
    appellation: Optional[str] = None
    appellationType: Optional[str] = None
    toponym: Optional[str] = None


# In[5]:


@dataclass
class ActiveAs(PersonAttributeLocation):
    """Represents an activity associated with a person."""
    activity: Optional[str] = None
    activityType: Optional[str] = None
    employer: Optional[str] = None


# In[6]:


@dataclass
class Identity(PersonAttributeLocation):
    """Represents an identity associated with a person."""
    identity: Optional[str] = None
    identityType: Optional[str] = None


# In[7]:


@dataclass
class Status(PersonAttributeLocation):
    """Represents a status associated with a person."""
    status: Optional[str] = None
    statusType: Optional[str] = None


# In[8]:


@dataclass
class LocationRelation(PersonAttributeLocation):
    """Represents a location relation associated with a person."""
    locationRelation: Optional[str] = None


# In[9]:


@dataclass
class Relation(PersonAttribute):
    """Represents a relation between two people."""
    relation: Optional[str] = None
    otherPerson: Optional[str] = None


# In[10]:


@dataclass
class Event(PersonAttributeLocation):
    """Represents an event associated with a person."""
    event: Optional[str] = None
    argument: Optional[str] = None


# In[11]:


@dataclass
class ExternalReference:
    """Represents an external reference to a person in another database."""
    id: Optional[int] = None
    URI: str = ""
    reconstruction_id: Optional[str] = None
    external_db_name: Optional[str] = None
    external_id: Optional[str] = None
    external_id_type: Optional[str] = None


# In[25]:


@dataclass
class Person:
    """Represents a person entity."""
    id: Optional[int] = None
    URI: str = ""
    comment: Optional[str] = None
    
    # Relationships (populated after initialization)
    active_as: List[ActiveAs] = field(default_factory=list)
    appellations: List[Appellation] = field(default_factory=list)
    identities: List[Identity] = field(default_factory=list)
    statuses: List[Status] = field(default_factory=list)
    location_relations: List[LocationRelation] = field(default_factory=list)
    relations: List[Relation] = field(default_factory=list)
    events: List[Event] = field(default_factory=list)
    external_references: List[ExternalReference] = field(default_factory=list)
    
    def split_values(self, attribute_name: str, field_name: str, separators: List[str], unused_remains: List[str], exceptions: List[str]):
        """
        Splits values in a specified field of PersonAttribute instances into multiple instances,
        using defined separators. Filters out unwanted values and respects exception list.
        
        Args:
            attribute_name: Name of the list of PersonAttribute instances (e.g. 'active_as')
            field_name: Name of the field in those instances to split (e.g. 'location')
            separators: List of substrings to split the value on
            unused_remains: List of split values to ignore/remove
            exceptions: List of full values that should not be split
        """
        
        #first check if it is a valid request
        attr_list = getattr(self, attribute_name, None)
        if not isinstance(attr_list, list):
            raise AttributeError(f"{attribute_name} is not a valid Person Attribute")
        
        #then check if there is anything in the list
        if not attr_list:
            return
        
        #then check if the field value is legit
        if not hasattr(attr_list[0], field_name):
            raise AttributeError(f"{field_name} is not a valid field for {attribute_name}")
        
        #make a new list
        new_p_attrs = []
        
        #check against exceptions
        for a in attr_list:
            value = getattr(a, field_name)
            if not value or value.strip() in exceptions:
                new_p_attrs.append(a)
                continue
        
            #split
            split_parts = [value]
            
            for sep in separators:
                split_parts = [part.strip() for val in split_parts for part in val.split(sep)]
                
            # Filter out unused_remains
            split_parts = [part for part in split_parts if part and part not in unused_remains]    

            #for every split do a deepcopy, alter and append
            if len(split_parts) <= 1:
                new_p_attrs.append(a)
                
            else:
                for part in split_parts:
                    new_attr = copy.deepcopy(a)
                    setattr(new_attr, field_name, part)
                    new_p_attrs.append(new_attr)
        
        #replace old with new
        setattr(self, attribute_name, new_p_attrs)
        
    
    def link_values(self, mapping: dict, attribute_name: str, field_name: str, log_file: str = "unmatched_values.txt"):
        """
        Replaces values in a specified attribute, in a specifiec field, with the mapped values in a dictionary.
        Logs any keyerrors to a file.
        
        Args:
            mapping: a dictionary containing key:value pairs linking a string to an URI or other external identifier.
            attribute_name: the person attribute (e.g. appellation, or activeAs) that you want to link a value in
            field_name: the field within the attribute (e.g. activity, or location, or appellationType) that 
            you want to link using the dict
            log_file: where key errors will be logged as they need a future mapping
        """
        
        #first check if it is a valid request
        attr_list = getattr(self, attribute_name, None)
        if not isinstance(attr_list, list):
            raise AttributeError(f"{attribute_name} is not a valid Person Attribute")
        
        #then check if there is anything in the list
        if not attr_list:
            return
        
        #then check if the field value is legit
        if not hasattr(attr_list[0], field_name):
            raise AttributeError(f"{field_name} is not a valid field for {attribute_name}")
        
        unmatched = set()
        
        for attr in attr_list:
            current_value = getattr(attr, field_name)
            if current_value in mapping:
                setattr(attr, field_name, mapping[current_value])
            elif current_value is not None:
                unmatched.add(current_value)
                
        if unmatched:
            with open(log_file, "a", encoding="utf-8") as f:
                for val in unmatched:
                    f.write("{val}\n")


# In[26]:


@dataclass
class PersonList:
    """A dataclass representing a list of Person objects with utility methods."""
    #default factory just initiates an empty list
    persons: List[Person] = field(default_factory=list)
    
    def __post_init__(self):
        #validate that all items in the list are Person objects
        if not all(isinstance(a, Person) for a in self.persons):
            raise TypeError("This object must consist of a list of Person objects")
    
    @staticmethod
    def _format_value(value):
        """convert None values to '-1 for CSV export"""
        return '-1' if value is None else value
    
    def split_list_valuessplit_values(self, attribute_name: str, field_name: str, separators: List[str], unused_remains: List[str], exceptions: List[str]):
        for p in self.persons:
            p.link_valuessplit_values(self, attribute_name, field_name, separators, unused_remains, exceptions)
    
    def link_list_values(self, mapping: dict, attribute_name: str, field_name: str, log_file: str = "unmatched_values.txt"):
        """
        Replaces values in a specified attribute, in a specifiec field, with the mapped values in a dictionary.
        Logs any keyerrors to a file.
        
        Args:
            mapping: a dictionary containing key:value pairs linking a string to an URI or other external identifier.
            attribute_name: the person attribute (e.g. appellation, or activeAs) that you want to link a value in
            field_name: the field within the attribute (e.g. activity, or location, or appellationType) that 
            you want to link using the dict
            log_file: where key errors will be logged that need to get a mapping
        """
        
        for p in self.persons:
            p.link_values(mapping, attribute_name, field_name, log_file)
    
    def to_csv(self, makeOverview=True, makeAppellations=True, makeActive_as=True, makeIdentities=True, makeStatuses=True, makeLocation_relations=True, makeRelations=True, makeEvents=True, makeExternalReferences=True):
        """
        Export person data to CSV files.

        Parameters:
        - makeOverview: Whether to create an overview CSV with basic person data
        - makeAppellations: Whether to create a CSV with appellation data
        - makeActive_as: Whether to create a CSV with activity data
        - makeIdentities: Whether to create a CSV with identity data
        - makeStatuses: Whether to create a CSV with status data
        - makeLocation_relations: Whether to create a CSV with location relation data
        - makeRelations: Whether to create a CSV with relation data
        - makeEvents: Whether to create a CSV with event data
        - makeExternalReferences: Whether to create a CSV with external reference data
    """
    
        if makeOverview:

            overviewFrame = []

            for p in self.persons:
                overviewFrame.append([p.URI, self._format_value(p.comment)])
            overviewFrame = pd.DataFrame(overviewFrame, columns=['URI', 'Comment'])
            overviewFrame.to_csv('overview.csv')

        if makeAppellations:
            appellationsFrame = []
            for p in self.persons:
                for a in p.appellations:
                    appellationsFrame.append([
                        p.URI,
                        self._format_value(a.observation_id),
                        self._format_value(a.reconstruction_id),
                        self._format_value(a.appellation),
                        self._format_value(a.appellationType),
                        self._format_value(a.annotationDate),
                        self._format_value(a.startDate),
                        self._format_value(a.endDate),
                        self._format_value(a.startDate_min),
                        self._format_value(a.startDate_max),
                        self._format_value(a.endDate_min),
                        self._format_value(a.endDate_max),
                        self._format_value(a.toponym),
                        self._format_value(a.observation_source),
                        self._format_value(a.location_in_observation_source),
                        self._format_value(a.reconstruction_source),
                        self._format_value(a.location_in_reconstruction_source),
                        self._format_value(a.comment)
                    ])
            appellationsFrame = pd.DataFrame(appellationsFrame, 
                                           columns=['URI', 'Observation', 'Reconstruction', 'Appellation', 
                                                   'AppellationType', 'AnnotationDate', 'StartDate', 'EndDate',
                                                   'StartDate_Min', 'StartDate_Max', 'EndDate_Min', 'EndDate_Max',
                                                   'Toponym', 'Observation source', 'Location in Observation Source', 
                                                   'Reconstruction Source', 'Location in Reconstruction Source', 'Comment'])
            appellationsFrame.to_csv('appellations.csv')

        if makeActive_as:
            activeAsFrame = []
            for p in self.persons:
                for a in p.active_as:
                    activeAsFrame.append([
                        p.URI,
                        self._format_value(a.observation_id),
                        self._format_value(a.reconstruction_id),
                        self._format_value(a.original_label),
                        self._format_value(a.activity),
                        self._format_value(a.activityType),
                        self._format_value(a.employer),
                        self._format_value(a.location),
                        self._format_value(a.annotationDate),
                        self._format_value(a.startDate),
                        self._format_value(a.endDate),
                        self._format_value(a.startDate_min),
                        self._format_value(a.startDate_max),
                        self._format_value(a.endDate_min),
                        self._format_value(a.endDate_max),
                        self._format_value(a.observation_source),
                        self._format_value(a.location_in_observation_source),
                        self._format_value(a.reconstruction_source),
                        self._format_value(a.location_in_reconstruction_source),
                        self._format_value(a.comment)
                    ])
            activeAsFrame = pd.DataFrame(activeAsFrame, 
                                       columns=['URI', 'Observation', 'Reconstruction', 'Original Label', 
                                               'Activity', 'ActivityType', 'Employer', 'Location', 
                                               'AnnotationDate', 'StartDate', 'EndDate',
                                               'StartDate_Min', 'StartDate_Max', 'EndDate_Min', 'EndDate_Max',
                                               'Observation source', 'Location in Observation Source', 'Reconstruction Source', 
                                               'Location in Reconstruction Source', 'Comment'])
            activeAsFrame.to_csv('activities.csv')

        if makeIdentities:
            identitiesFrame = []
            for p in self.persons:
                for identity in p.identities:
                    identitiesFrame.append([
                        p.URI,
                        self._format_value(identity.observation_id),
                        self._format_value(identity.reconstruction_id),
                        self._format_value(identity.original_label),
                        self._format_value(identity.identity),
                        self._format_value(identity.identityType),
                        self._format_value(identity.location),
                        self._format_value(identity.annotationDate),
                        self._format_value(identity.startDate),
                        self._format_value(identity.endDate),
                        self._format_value(identity.startDate_min),
                        self._format_value(identity.startDate_max),
                        self._format_value(identity.endDate_min),
                        self._format_value(identity.endDate_max),
                        self._format_value(identity.observation_source),
                        self._format_value(identity.location_in_observation_source),
                        self._format_value(identity.reconstruction_source),
                        self._format_value(identity.location_in_reconstruction_source),
                        self._format_value(identity.comment)
                    ])
            identitiesFrame = pd.DataFrame(identitiesFrame, 
                                         columns=['URI', 'Observation', 'Reconstruction', 'Original Label', 
                                                 'Identity', 'IdentityType', 'Location', 'AnnotationDate', 
                                                 'StartDate', 'EndDate',
                                                 'StartDate_Min', 'StartDate_Max', 'EndDate_Min', 'EndDate_Max',
                                                 'Observation source', 'Location in Observation Source',
                                                 'Reconstruction Source', 'Location in Reconstruction Source', 'Comment'])
            identitiesFrame.to_csv('identities.csv')

        if makeStatuses:
            statusesFrame = []
            for p in self.persons:
                for status in p.statuses:
                    statusesFrame.append([
                        p.URI,
                        self._format_value(status.observation_id),
                        self._format_value(status.reconstruction_id),
                        self._format_value(status.original_label),
                        self._format_value(status.status),
                        self._format_value(status.statusType),
                        self._format_value(status.location),
                        self._format_value(status.annotationDate),
                        self._format_value(status.startDate),
                        self._format_value(status.endDate),
                        self._format_value(status.startDate_min),
                        self._format_value(status.startDate_max),
                        self._format_value(status.endDate_min),
                        self._format_value(status.endDate_max),
                        self._format_value(status.observation_source),
                        self._format_value(status.location_in_observation_source),
                        self._format_value(status.reconstruction_source),
                        self._format_value(status.location_in_reconstruction_source),
                        self._format_value(status.comment)
                    ])
            statusesFrame = pd.DataFrame(statusesFrame, 
                                       columns=['URI', 'Observation', 'Reconstruction', 'Original Label', 
                                               'Status', 'StatusType', 'Location', 'AnnotationDate', 
                                               'StartDate', 'EndDate',
                                               'StartDate_Min', 'StartDate_Max', 'EndDate_Min', 'EndDate_Max',
                                               'Observation source', 'Location in Observation Source',
                                               'Reconstruction Source', 'Location in Reconstruction Source', 'Comment'])
            statusesFrame.to_csv('statuses.csv')

        if makeLocation_relations:
            locationRelationFrame = []
            for p in self.persons:
                for lr in p.location_relations:
                    locationRelationFrame.append([
                        p.URI,
                        self._format_value(lr.observation_id),
                        self._format_value(lr.reconstruction_id),
                        self._format_value(lr.original_label),
                        self._format_value(lr.locationRelation),
                        self._format_value(lr.location),
                        self._format_value(lr.annotationDate),
                        self._format_value(lr.startDate),
                        self._format_value(lr.endDate),
                        self._format_value(lr.startDate_min),
                        self._format_value(lr.startDate_max),
                        self._format_value(lr.endDate_min),
                        self._format_value(lr.endDate_max),
                        self._format_value(lr.observation_source),
                        self._format_value(lr.location_in_observation_source),
                        self._format_value(lr.reconstruction_source),
                        self._format_value(lr.location_in_reconstruction_source),
                        self._format_value(lr.comment)
                    ])
            locationRelationFrame = pd.DataFrame(locationRelationFrame, 
                                              columns=['URI', 'Observation', 'Reconstruction', 'Original Label', 
                                                     'LocationRelation', 'Location', 'AnnotationDate', 
                                                     'StartDate', 'EndDate',
                                                     'StartDate_Min', 'StartDate_Max', 'EndDate_Min', 'EndDate_Max',
                                                     'Observation source', 'Location in Observation Source',
                                                     'Reconstruction Source', 'Location in Reconstruction Source', 'Comment'])
            locationRelationFrame.to_csv('locationRelations.csv')

        if makeRelations:
            relationsFrame = []
            for p in self.persons:
                for r in p.relations:
                    relationsFrame.append([
                        p.URI,
                        self._format_value(r.observation_id),
                        self._format_value(r.reconstruction_id),
                        self._format_value(r.original_label),
                        self._format_value(r.relation),
                        self._format_value(r.otherPerson),
                        self._format_value(r.annotationDate),
                        self._format_value(r.startDate),
                        self._format_value(r.endDate),
                        self._format_value(r.startDate_min),
                        self._format_value(r.startDate_max),
                        self._format_value(r.endDate_min),
                        self._format_value(r.endDate_max),
                        self._format_value(r.observation_source),
                        self._format_value(r.location_in_observation_source),
                        self._format_value(r.reconstruction_source),
                        self._format_value(r.location_in_reconstruction_source),
                        self._format_value(r.comment)
                    ])
            relationsFrame = pd.DataFrame(relationsFrame, 
                                       columns=['URI', 'Observation', 'Reconstruction', 'Original Label', 
                                               'Relation', 'OtherPerson', 'AnnotationDate', 'StartDate', 
                                               'EndDate',
                                               'StartDate_Min', 'StartDate_Max', 'EndDate_Min', 'EndDate_Max',
                                               'Observation source', 'Location in Observation Source',
                                               'Reconstruction Source', 'Location in Reconstruction Source', 'Comment'])     
            relationsFrame.to_csv('relations.csv')

        if makeEvents:
            eventsFrame = []
            for p in self.persons:
                for e in p.events:
                    eventsFrame.append([
                        p.URI,
                        self._format_value(e.observation_id),
                        self._format_value(e.reconstruction_id),
                        self._format_value(e.original_label),
                        self._format_value(e.event),
                        self._format_value(e.argument),
                        self._format_value(e.location),
                        self._format_value(e.annotationDate),
                        self._format_value(e.startDate),
                        self._format_value(e.endDate),
                        self._format_value(e.startDate_min),
                        self._format_value(e.startDate_max),
                        self._format_value(e.endDate_min),
                        self._format_value(e.endDate_max),
                        self._format_value(e.observation_source),
                        self._format_value(e.location_in_observation_source),
                        self._format_value(e.reconstruction_source),
                        self._format_value(e.location_in_reconstruction_source),
                        self._format_value(e.comment)
                    ])
            eventsFrame = pd.DataFrame(eventsFrame, 
                                     columns=['URI', 'Observation', 'Reconstruction', 'Original Label', 
                                             'Event', 'Argument', 'Location', 'AnnotationDate', 
                                             'StartDate', 'EndDate',
                                             'StartDate_Min', 'StartDate_Max', 'EndDate_Min', 'EndDate_Max',
                                             'Observation source', 'Location in Observation Source',
                                             'Reconstruction Source', 'Location in Reconstruction Source', 'Comment'])
            eventsFrame.to_csv('events.csv')

        if makeExternalReferences:
            externalReferencesFrame = []
            for p in self.persons:
                for ref in p.external_references:
                    externalReferencesFrame.append([
                        p.URI,
                        self._format_value(ref.reconstruction_id),
                        self._format_value(ref.external_db_name),
                        self._format_value(ref.external_id),
                        self._format_value(ref.external_id_type)
                    ])
            externalReferencesFrame = pd.DataFrame(externalReferencesFrame, 
                                                columns=['URI', 'Reconstruction ID', 'External DB Name', 
                                                        'External ID', 'External ID Type'])
            externalReferencesFrame.to_csv('external_references.csv')    
        
    def update_db(self, db, makeOverview=True, makeAppellations=True, makeActive_as=True, 
                 makeIdentities=True, makeStatuses=True, makeLocation_relations=True, 
                 makeRelations=True, makeEvents=True, makeExternalReferences=True):

        # Create engine
        engine = create_engine(f'sqlite:///{db}')
        metadata = MetaData(f'sqlite:///{db}')

        # Copy the .schema into the metadata
        metadata.reflect(bind=engine)

        # Create a session with autoflush off
        Session = sessionmaker(bind=engine, autoflush=False)
        session = Session()

        # For each table, check if it needs to be constructed
        if makeOverview:
            # If so, connect the table to a variable
            overview_table = metadata.tables['persons']

            # Create an empty object to bind to the table
            class Overview_sql(object): pass

            # Map table to object
            mapper(Overview_sql, overview_table)

            for p in tqdm(self.persons):
                new_overview_sql = Overview_sql()
                new_overview_sql.URI = p.URI
                new_overview_sql.comment = p.comment
                session.merge(new_overview_sql)

        if makeAppellations:
            # If so, connect the table to a variable
            appellation_table = metadata.tables['appellations']

            # Create an empty object to bind to the table
            class Appellation_sql(object): pass

            # Map table to object
            mapper(Appellation_sql, appellation_table)

            for p in tqdm(self.persons):
                for a in p.appellations:
                    new_appellation_sql = Appellation_sql()
                    new_appellation_sql.URI = p.URI
                    new_appellation_sql.observation_id = a.observation_id
                    new_appellation_sql.reconstruction_id = a.reconstruction_id
                    new_appellation_sql.appellation = a.appellation
                    new_appellation_sql.appellationType = a.appellationType
                    new_appellation_sql.annotationDate = a.annotationDate
                    new_appellation_sql.startDate = a.startDate
                    new_appellation_sql.endDate = a.endDate
                    new_appellation_sql.startDate_min = a.startDate_min
                    new_appellation_sql.startDate_max = a.startDate_max
                    new_appellation_sql.endDate_min = a.endDate_min
                    new_appellation_sql.endDate_max = a.endDate_max
                    new_appellation_sql.toponym = a.toponym
                    new_appellation_sql.observation_source = a.observation_source
                    new_appellation_sql.location_in_observation_source = a.location_in_observation_source
                    new_appellation_sql.reconstruction_source = a.reconstruction_source
                    new_appellation_sql.location_in_reconstruction_source = a.location_in_reconstruction_source
                    new_appellation_sql.comment = a.comment

                    session.merge(new_appellation_sql)

        if makeActive_as:
            # If so, connect the table to a variable
            activeAs_table = metadata.tables['activeAs']

            # Create an empty object to bind to the table
            class activeAs_sql(object): pass

            # Map table to object
            mapper(activeAs_sql, activeAs_table)

            for p in tqdm(self.persons):
                for a in p.active_as:
                    new_activeAs_sql = activeAs_sql()
                    new_activeAs_sql.URI = p.URI
                    new_activeAs_sql.observation_id = a.observation_id
                    new_activeAs_sql.reconstruction_id = a.reconstruction_id
                    new_activeAs_sql.original_label = a.original_label
                    new_activeAs_sql.activity = a.activity
                    new_activeAs_sql.activityType = a.activityType
                    new_activeAs_sql.employer = a.employer
                    new_activeAs_sql.annotationDate = a.annotationDate
                    new_activeAs_sql.startDate = a.startDate
                    new_activeAs_sql.endDate = a.endDate
                    new_activeAs_sql.startDate_min = a.startDate_min
                    new_activeAs_sql.startDate_max = a.startDate_max
                    new_activeAs_sql.endDate_min = a.endDate_min
                    new_activeAs_sql.endDate_max = a.endDate_max
                    new_activeAs_sql.location = a.location
                    new_activeAs_sql.observation_source = a.observation_source
                    new_activeAs_sql.location_in_observation_source = a.location_in_observation_source
                    new_activeAs_sql.reconstruction_source = a.reconstruction_source
                    new_activeAs_sql.location_in_reconstruction_source = a.location_in_reconstruction_source
                    new_activeAs_sql.comment = a.comment

                    session.merge(new_activeAs_sql)

        if makeIdentities:
            # If so, connect the table to a variable
            identities_table = metadata.tables['identities']

            # Create an empty object to bind to the table
            class Identity_sql(object): pass

            # Map table to object
            mapper(Identity_sql, identities_table)

            for p in tqdm(self.persons):
                for a in p.identities:
                    new_Identity_sql = Identity_sql()
                    new_Identity_sql.URI = p.URI
                    new_Identity_sql.observation_id = a.observation_id
                    new_Identity_sql.reconstruction_id = a.reconstruction_id
                    new_Identity_sql.original_label = a.original_label
                    new_Identity_sql.identity = a.identity
                    new_Identity_sql.identityType = a.identityType
                    new_Identity_sql.annotationDate = a.annotationDate
                    new_Identity_sql.startDate = a.startDate
                    new_Identity_sql.endDate = a.endDate
                    new_Identity_sql.startDate_min = a.startDate_min
                    new_Identity_sql.startDate_max = a.startDate_max
                    new_Identity_sql.endDate_min = a.endDate_min
                    new_Identity_sql.endDate_max = a.endDate_max
                    new_Identity_sql.location = a.location
                    new_Identity_sql.observation_source = a.observation_source
                    new_Identity_sql.location_in_observation_source = a.location_in_observation_source
                    new_Identity_sql.reconstruction_source = a.reconstruction_source
                    new_Identity_sql.location_in_reconstruction_source = a.location_in_reconstruction_source
                    new_Identity_sql.comment = a.comment

                    session.merge(new_Identity_sql)

        if makeStatuses:
            # If so, connect the table to a variable
            statuses_table = metadata.tables['statuses']

            # Create an empty object to bind to the table
            class Status_sql(object): pass

            # Map table to object
            mapper(Status_sql, statuses_table)

            for p in tqdm(self.persons):
                for a in p.statuses:
                    new_Status_sql = Status_sql()
                    new_Status_sql.URI = p.URI
                    new_Status_sql.observation_id = a.observation_id
                    new_Status_sql.reconstruction_id = a.reconstruction_id
                    new_Status_sql.original_label = a.original_label
                    new_Status_sql.status = a.status
                    new_Status_sql.statusType = a.statusType
                    new_Status_sql.annotationDate = a.annotationDate
                    new_Status_sql.startDate = a.startDate
                    new_Status_sql.endDate = a.endDate
                    new_Status_sql.startDate_min = a.startDate_min
                    new_Status_sql.startDate_max = a.startDate_max
                    new_Status_sql.endDate_min = a.endDate_min
                    new_Status_sql.endDate_max = a.endDate_max
                    new_Status_sql.location = a.location
                    new_Status_sql.observation_source = a.observation_source
                    new_Status_sql.location_in_observation_source = a.location_in_observation_source
                    new_Status_sql.reconstruction_source = a.reconstruction_source
                    new_Status_sql.location_in_reconstruction_source = a.location_in_reconstruction_source
                    new_Status_sql.comment = a.comment

                    session.merge(new_Status_sql)      

        if makeLocation_relations:
            # If so, connect the table to a variable
            locationRelations_table = metadata.tables['locationRelations']

            # Create an empty object to bind to the table
            class locationRelation_sql(object): pass

            # Map table to object
            mapper(locationRelation_sql, locationRelations_table)

            for p in tqdm(self.persons):
                for a in p.location_relations:
                    new_locationRelation_sql = locationRelation_sql()
                    new_locationRelation_sql.URI = p.URI
                    new_locationRelation_sql.observation_id = a.observation_id
                    new_locationRelation_sql.reconstruction_id = a.reconstruction_id
                    new_locationRelation_sql.original_label = a.original_label
                    new_locationRelation_sql.annotationDate = a.annotationDate
                    new_locationRelation_sql.startDate = a.startDate
                    new_locationRelation_sql.endDate = a.endDate
                    new_locationRelation_sql.startDate_min = a.startDate_min
                    new_locationRelation_sql.startDate_max = a.startDate_max
                    new_locationRelation_sql.endDate_min = a.endDate_min
                    new_locationRelation_sql.endDate_max = a.endDate_max
                    new_locationRelation_sql.location = a.location
                    new_locationRelation_sql.observation_source = a.observation_source
                    new_locationRelation_sql.locationRelation = a.locationRelation
                    new_locationRelation_sql.location_in_observation_source = a.location_in_observation_source
                    new_locationRelation_sql.reconstruction_source = a.reconstruction_source
                    new_locationRelation_sql.location_in_reconstruction_source = a.location_in_reconstruction_source
                    new_locationRelation_sql.comment = a.comment

                    session.merge(new_locationRelation_sql)   

        if makeRelations:
            # If so, connect the table to a variable
            relations_table = metadata.tables['relations']

            # Create an empty object to bind to the table
            class relation_sql(object): pass

            # Map table to object
            mapper(relation_sql, relations_table)

            for p in tqdm(self.persons):
                for a in p.relations:
                    new_relation_sql = relation_sql()
                    new_relation_sql.URI = p.URI
                    new_relation_sql.observation_id = a.observation_id
                    new_relation_sql.reconstruction_id = a.reconstruction_id
                    new_relation_sql.original_label = a.original_label
                    new_relation_sql.otherPerson = a.otherPerson
                    new_relation_sql.relation = a.relation
                    new_relation_sql.annotationDate = a.annotationDate
                    new_relation_sql.startDate = a.startDate
                    new_relation_sql.endDate = a.endDate
                    new_relation_sql.startDate_min = a.startDate_min
                    new_relation_sql.startDate_max = a.startDate_max
                    new_relation_sql.endDate_min = a.endDate_min
                    new_relation_sql.endDate_max = a.endDate_max
                    new_relation_sql.observation_source = a.observation_source
                    new_relation_sql.location_in_observation_source = a.location_in_observation_source
                    new_relation_sql.reconstruction_source = a.reconstruction_source
                    new_relation_sql.location_in_reconstruction_source = a.location_in_reconstruction_source
                    new_relation_sql.comment = a.comment

                    session.merge(new_relation_sql)   

        if makeEvents:
            events_table = metadata.tables['events']

            class event_sql(object): pass

            # Map table to object
            mapper(event_sql, events_table)

            for p in tqdm(self.persons):
                for a in p.events:
                    new_event_sql = event_sql()
                    new_event_sql.URI = p.URI
                    new_event_sql.observation_id = a.observation_id
                    new_event_sql.reconstruction_id = a.reconstruction_id
                    new_event_sql.original_label = a.original_label
                    new_event_sql.event = a.event
                    new_event_sql.argument = a.argument
                    new_event_sql.annotationDate = a.annotationDate
                    new_event_sql.startDate = a.startDate
                    new_event_sql.endDate = a.endDate
                    new_event_sql.startDate_min = a.startDate_min
                    new_event_sql.startDate_max = a.startDate_max
                    new_event_sql.endDate_min = a.endDate_min
                    new_event_sql.endDate_max = a.endDate_max
                    new_event_sql.location = a.location
                    new_event_sql.observation_source = a.observation_source
                    new_event_sql.location_in_observation_source = a.location_in_observation_source
                    new_event_sql.reconstruction_source = a.reconstruction_source
                    new_event_sql.location_in_reconstruction_source = a.location_in_reconstruction_source
                    new_event_sql.comment = a.comment

                    session.merge(new_event_sql)

        if makeExternalReferences:
            external_references_table = metadata.tables['externalReferences']

            class external_reference_sql(object): pass

            # Map table to object
            mapper(external_reference_sql, external_references_table)

            for p in tqdm(self.persons):
                for a in p.external_references:
                    new_external_reference_sql = external_reference_sql()
                    new_external_reference_sql.URI = p.URI
                    new_external_reference_sql.reconstruction_id = a.reconstruction_id
                    new_external_reference_sql.external_db_name = a.external_db_name
                    new_external_reference_sql.external_id = a.external_id
                    new_external_reference_sql.external_id_type = a.external_id_type

                    session.merge(new_external_reference_sql)

        # After all that

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




