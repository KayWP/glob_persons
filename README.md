# GLOB_Persons

A Python library for managing historical person data with attributes like appellations, activities, identities, and relationships. This system provides a structured way to handle complex biographical information with validation, data processing, and export capabilities.

## Overview

This library defines a hierarchical data model for representing persons and their various attributes throughout history. It's designed for digital humanities projects, genealogical research, or any application requiring structured biographical data management.

## Features

- **Structured Data Models**: Comprehensive dataclasses for persons and their attributes
- **Date Validation**: ISO 8601 compliant date validation with flexible formats
- **Data Processing**: Value splitting, linking, and transformation utilities
- **Export Capabilities**: CSV and SQLite database export functionality
- **Data Integrity**: Automatic lowercasing and validation of input data

## Installation

### Dependencies

```bash
pip install pandas sqlalchemy tqdm
```

### Standard Library Dependencies
- `dataclasses`
- `typing` 
- `copy`
- `datetime`

## Data Model

### Core Classes

#### `PersonAttribute` (Base Class)
Base class for all person-related observations with common fields:
- `id`, `observation_id`, `reconstruction_id`
- Date fields: `annotationDate`, `startDate`, `endDate` (with min/max variants)
- Source tracking: `observation_source`, `reconstruction_source`
- Location references and comments

#### `Person`
Central entity representing an individual with:
- Basic info: `id`, `URI`, `comment`
- Collections of related attributes:
  - `appellations` - names and titles
  - `active_as` - activities and occupations
  - `identities` - social/cultural identities
  - `statuses` - social/legal statuses
  - `location_relations` - geographic relationships
  - `relations` - relationships with other persons
  - `events` - life events
  - `external_references` - links to other databases

#### Specialized Attribute Classes
- **`Appellation`**: Names, titles, and appellations
- **`ActiveAs`**: Professional activities and employment
- **`Identity`**: Cultural, religious, or social identities
- **`Status`**: Legal, social, or economic status
- **`LocationRelation`**: Geographic relationships
- **`Relation`**: Interpersonal relationships
- **`Event`**: Life events and occurrences
- **`ExternalReference`**: Links to external databases

#### `PersonList`
Container class for managing collections of `Person` objects with batch operations.

## Usage Examples

### Basic Person Creation

```python
from your_module import Person, Appellation, ActiveAs

# Create a person
person = Person(
    URI="https://example.com/person/1",
    comment="Historical figure from 15th century"
)

# Add an appellation
appellation = Appellation(
    appellation="John Smith",
    appellationType="given name",
    startDate="1450",
    endDate="1500"
)
person.appellations.append(appellation)

# Add an activity
activity = ActiveAs(
    activity="merchant",
    activityType="occupation",
    location="London",
    startDate="1470",
    endDate="1495"
)
person.active_as.append(activity)
```

### Working with PersonList

```python
from your_module import PersonList

# Create a collection
person_list = PersonList(persons=[person1, person2, person3])

# Export to CSV files
person_list.to_csv(
    makeOverview=True,
    makeAppellations=True,
    makeActive_as=True
)

# Link values using a mapping dictionary
mapping = {
    "merchant": "https://vocab.example.com/merchant",
    "london": "https://geonames.org/london"
}
person_list.link_list_values(
    mapping=mapping,
    attribute_name="active_as",
    field_name="activity"
)
```

### Date Validation

The system automatically validates dates in ISO 8601 format:

```python
# Valid formats:
# - "1450" (year only)
# - "1450-03" (year-month)
# - "1450-03-15" (full date)
# - "-1" (unknown date - converted to None)

appellation = Appellation(
    appellation="Historical Name",
    startDate="1450-03",  # Valid
    endDate="invalid-date"  # Raises ValueError
)
```

### Data Processing

```python
# Split composite values
person.split_values(
    attribute_name="active_as",
    field_name="location",
    separators=[",", ";", " and "],
    unused_remains=["unknown", ""],
    exceptions=["London, England"]  # Don't split these
)

# Link values to URIs
mapping = import_linking_list("location_mappings.csv")
person.link_values(
    mapping=mapping,
    attribute_name="active_as",
    field_name="location",
    log_file="unmatched_locations.txt"
)
```

### Database Export

```python
# Export to SQLite database
person_list.update_db(
    db="historical_persons.sqlite",
    makeOverview=True,
    makeAppellations=True,
    makeActive_as=True
)
```

## Data Validation

### Automatic Processing
- All string fields (except `original_label`) are automatically converted to lowercase
- Date fields are validated against ISO 8601 formats
- Invalid dates raise `ValueError` with descriptive messages

### Date Formats
Supported formats:
- `YYYY` (e.g., "1450")
- `YYYY-MM` (e.g., "1450-03") 
- `YYYY-MM-DD` (e.g., "1450-03-15")
- `"-1"` for unknown dates (converted to `None`)

## Export Formats

### CSV Export
The `to_csv()` method generates separate CSV files for each attribute type:
- `overview.csv` - Basic person information
- `appellations.csv` - Names and titles
- `activities.csv` - Professional activities
- `identities.csv` - Social identities
- `statuses.csv` - Legal/social statuses
- `locationRelations.csv` - Geographic relationships
- `relations.csv` - Interpersonal relationships
- `events.csv` - Life events
- `external_references.csv` - External database links

### Database Export
The `update_db()` method exports data to SQLite database tables with the same structure as CSV exports.

## Utility Functions

### `import_linking_list(filename)`
Imports a CSV file with `original_label` and `URI` columns to create a mapping dictionary for data linking.

```python
# CSV format:
# original_label,URI
# merchant,https://vocab.example.com/merchant
# london,https://geonames.org/london

mapping = import_linking_list("mappings.csv")
```

## Error Handling

The system provides detailed error messages for:
- Invalid date formats
- Missing required fields
- Incorrect attribute names
- Database connection issues

## Best Practices

1. **Date Consistency**: Use ISO 8601 formats consistently
2. **URI Standards**: Use stable, dereferenceable URIs for person identifiers
3. **Data Validation**: Validate input data before creating objects
4. **Batch Processing**: Use `PersonList` for operations on multiple persons
5. **Source Documentation**: Always populate source and location fields for data provenance

## Contributing

When extending this library:
- Follow the existing dataclass patterns
- Add appropriate validation in `__post_init__` methods
- Update export methods for new fields
- Maintain backward compatibility
- Add comprehensive docstrings

## License

[Add your license information here]

## Version History

- Initial version: Comprehensive person data management system with export capabilities
