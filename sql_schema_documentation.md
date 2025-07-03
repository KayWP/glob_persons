
# SQL Schema Documentation

This document describes the structure and relationships of the SQL schema used for representing people and their associated observations.

---

## `persons`

| Field Name | Type     | Relationship / Constraint | Description                        |
|------------|----------|----------------------------|------------------------------------|
| `id`       | INTEGER  | Primary Key                | Unique identifier for each person  |
| `URI`      | TEXT     | –                          | Unique identifier for a person     |
| `comment`  | TEXT     | –                          | Optional note or description       |

---

## `activeAs`

| Field Name                        | Type     | Relationship / Constraint                  | Description                                                |
|----------------------------------|----------|--------------------------------------------|------------------------------------------------------------|
| `id`                             | INTEGER  | Primary Key                                | Unique row ID                                              |
| `URI`                            | TEXT     | Foreign Key → `persons.URI`                | Refers to the person involved                              |
| `observation_id`                 | TEXT     | –                                          | Source observation identifier                              |
| `reconstruction_id`              | TEXT     | –                                          | Reconstructed instance identifier                          |
| `original_label`                 | TEXT     | –                                          | Original label in source                                   |
| `activity`                       | TEXT     | –                                          | Describes the activity (e.g., profession)                  |
| `activityType`                   | TEXT     | –                                          | Category of activity                                       |
| `employer`                       | TEXT     | –                                          | Employer mentioned in context                              |
| `location`                       | TEXT     | –                                          | Where the activity took place                              |
| `annotationDate`                 | TEXT     | –                                          | When the data was annotated                                |
| `startDate`, `endDate`          | TEXT     | –                                          | Main dates of activity                                     |
| `startDate_min`, `startDate_max`| TEXT     | –                                          | Lower and upper bounds for `startDate`                     |
| `endDate_min`, `endDate_max`    | TEXT     | –                                          | Lower and upper bounds for `endDate`                       |
| `observation_source`            | TEXT     | –                                          | Source document                                            |
| `location_in_observation_source`| TEXT     | –                                          | Where in the source document this was found                |
| `reconstruction_source`         | TEXT     | –                                          | Source used in reconstruction                              |
| `location_in_reconstruction_source`| TEXT  | –                                          | Location in reconstruction source                          |
| `comment`                        | TEXT     | –                                          | Additional information                                     |

---

## `appellations`

| Field Name                        | Type     | Relationship / Constraint                  | Description                                                |
|----------------------------------|----------|--------------------------------------------|------------------------------------------------------------|
| `appellation`                    | TEXT     | –                                          | Name or title given to a person                            |
| `appellationType`               | INT      | –                                          | Type/category of appellation                               |
| *Other fields:* Same as `activeAs` |          |                                            |                                                            |

---

## `identities`

| Field Name                        | Type     | Relationship / Constraint                  | Description                                                |
|----------------------------------|----------|--------------------------------------------|------------------------------------------------------------|
| `identity`                       | TEXT     | –                                          | Identity label (e.g., ethnicity)                           |
| `identityType`                   | TEXT     | –                                          | Category of identity                                       |
| *Other fields:* Same as `activeAs` |          |                                            |                                                            |

---

## `statuses`

| Field Name                        | Type     | Relationship / Constraint                  | Description                                                |
|----------------------------------|----------|--------------------------------------------|------------------------------------------------------------|
| `status`                         | TEXT     | –                                          | Status label (e.g., citizen, enslaved)                     |
| `statusType`                     | TEXT     | –                                          | Category of status                                         |
| *Other fields:* Same as `activeAs` |          |                                            |                                                            |

---

## `locationRelations`

| Field Name                        | Type     | Relationship / Constraint                  | Description                                                |
|----------------------------------|----------|--------------------------------------------|------------------------------------------------------------|
| `locationRelation`               | TEXT     | –                                          | Type of relation (e.g., resident_of)                       |
| *Other fields:* Same as `statuses` |          |                                            |                                                            |

---

## `relations`

| Field Name                        | Type     | Relationship / Constraint                  | Description                                                |
|----------------------------------|----------|--------------------------------------------|------------------------------------------------------------|
| `relation`                       | TEXT     | –                                          | Type of relation (e.g., parent, sibling)                   |
| `otherPerson`                    | TEXT     | Refers to another `persons.URI`            | The second person in the relationship                      |
| *Other fields:* Same as `statuses` |          |                                            |                                                            |

---

## `events`

| Field Name                        | Type     | Relationship / Constraint                  | Description                                                |
|----------------------------------|----------|--------------------------------------------|------------------------------------------------------------|
| `event`                          | TEXT     | –                                          | Type of event (e.g., birth, death)                         |
| `argument`                       | TEXT     | –                                          | Argument associated with the event (e.g., location)        |
| *Other fields:* Same as `statuses` |          |                                            |                                                            |

---

## `externalReferences`

| Field Name         | Type     | Relationship / Constraint         | Description                                                  |
|--------------------|----------|-----------------------------------|--------------------------------------------------------------|
| `id`               | INTEGER  | Primary Key                       | Unique ID for reference entry                                |
| `URI`              | TEXT     | Foreign Key → `persons.URI`       | Refers to the person                                         |
| `reconstruction_id`| TEXT     | –                                 | Associated reconstruction                                    |
| `external_db_name` | TEXT     | –                                 | Name of the external database                                |
| `external_id`      | TEXT     | –                                 | ID for the person in that external database                  |
| `external_id_type` | TEXT     | –                                 | Type of identifier (e.g., `URI`, `ID`)                       |
