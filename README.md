# Overview

The provided code is a Python module that defines classes and functions related to representing and working with person-related data, particularly attributes, appellations, activities, identities, statuses, relationships, and location relations. The module also includes a class for managing a list of persons. It includes a main function that will guide an user through the process of creating a person, then it exports the data to excel in a defined format. However, the code is mainly meant to be used as a package for the processing of large scale person datasets. It will be used by the GLOBALISE Project for the creation of a dataset on the Dutch East India Company.

### Function 'vali_date'
This function validates a date string against three standard date formats which are valid according to the ISO8601 standard: %Y (year), %Y-%m (year-month), and %Y-%m-%d (year-month-day). The function returns True if the date_string is valid according to one of the formats or if the date_string is -1 (used to indicate an unknown date). If the date_string does not match any of the formats, the function returns False.

### Function 'combine_lists'
This function combines two lists x and y into a new list z and returns the result. If both x and y are non-empty lists, z will be the concatenation of x and y. If one of the lists is empty, z will be the non-empty list, or an empty list if both x and y are empty.

### Class 'person_attribute'
This class represents a person attribute and serves as a base class for other specific person attributes like appellations, activities, identities, statuses, location relations, and relationships, which inherit its features. It has the following attributes:

- **annotation:** A date string representing when the attribute was recorded.
- **startdate:** A date string representing the start date of the attribute's validity.
- **enddate:** A date string representing the end date of the attribute's validity.
- **source:** A string representing the source of the attribute's information.

All of these values, except the source, can be unknown. The annotation date should as best practice not be unknown either.

### Class 'person_attribute_loc'
This class is a subclass of Person_attribute and represents a person attribute associated with a location. It adds a location attribute, which is a string representing the location associated with the attribute (which should ideally be an URI).

### Class Appellation
This class is a subclass of Person_attribute and represents an appellation attribute of a person. It adds two attributes:

- **app_str:** A string representing the appellation string.
- **app_type:** A string representing the appellation type.

### Class Activity
This class is a subclass of Person_attribute_loc and represents an activity attribute of a person. It adds three attributes:

- **function:** A string representing the function performed by the person.
- **function_type:** A string representing the type of function performed.
- **employer:** A string representing the employer associated with the activity.

Employer is optional.

### Class Identity
This class is a subclass of Person_attribute_loc and represents an identity attribute of a person. It adds two attributes:

**identifier:** A string representing the identifier associated with the person's identity.
- **identity_type:** A string representing the type of identity.

### Class Status
This class is a subclass of Person_attribute_loc and represents a status attribute of a person. It adds two attributes:

- **stat:** A string representing the status held by the person.
- **status_type:** A string representing the type of status.

### Class Location_Relation
This class is a subclass of Person_attribute_loc and represents a location relation attribute of a person. It adds one attribute:

- **location_relation:** A string representing the relation a person has to a specific location.

### Class Relation
This class is a subclass of Person_attribute and represents a relationship attribute of a person. It adds two attributes:

- **relation:** A string representing the relationship between the person and another person.
- **otherPerson:** A string representing the URI of the other person involved in the relationship.

### Class Person
This class represents a person and contains various attributes, including:

- **URI:** A string representing the unique identifier for the person.
- **DOB:** A string representing the date of birth of the person.
- **DOD:** A string representing the date of death of the person.
- **appellations:** A list of Appellation objects representing the person's appellations.
- **active_as:** A list of Activity objects representing the person's activities.
- **identified_as:** A list of Identity objects representing the person's identities.
- **status:** A list of Status objects representing the person's statuses.
- **relationships:** A list of Relationship objects representing the person's relationships with other persons.
- **location_relations:** A list of Location_Relation objects representing the person's relations to locations.

The class also includes methods for adding relationships to other persons and for merging the attributes of two persons with the same URI through an operator overload on the '+'.

### Class Personlist
This class represents a list of persons. It contains a list of Person objects and includes methods for merging persons with the same URI and exporting the person data to Excel files. The attributes and methods of this class are as follows:

- **persons:** A list of Person objects representing the persons in the list.
- **merge_on_uri():** A method that merges persons with the same URI in the list, combining their attributes into a single person.
- **to_excel():** A method that exports the person data to Excel files, with options to create separate sheets for different attributes like appellations, activities, identities, statuses, location relations, and relationships.