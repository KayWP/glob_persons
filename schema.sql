-- This table simply defines how many possible people there are in the dataset
CREATE TABLE IF NOT EXISTS "persons" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT,
    "URI" TEXT,
    "comment" TEXT
);

-- This table records observations of activities associated with a specific person
CREATE TABLE IF NOT EXISTS "activeAs" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT,
    "URI" TEXT,
    "observation_id" TEXT,
    "reconstruction_id" TEXT,
    "original_label" TEXT,
    "activity" TEXT,
    "activityType" TEXT,
    "employer" TEXT,
    "location" TEXT,
    "annotationDate" TEXT,
    "startDate" TEXT,
    "endDate" TEXT,
    "startDate_min" TEXT,
    "startDate_max" TEXT,
    "endDate_min" TEXT,
    "endDate_max" TEXT,
    "observation_source" TEXT,
    "location_in_observation_source" TEXT,
    "reconstruction_source" TEXT,
    "location_in_reconstruction_source" TEXT,
    "comment" TEXT,

    FOREIGN KEY("URI") REFERENCES "persons"("URI")
    );

-- This table records observations of appellations associated with a specific person
CREATE TABLE IF NOT EXISTS "appellations" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT,
    "URI" TEXT,
    "observation_id" TEXT,
    "reconstruction_id" TEXT,
    "appellation" TEXT,
    "appellationType" INT,
    "annotationDate" TEXT,
    "startDate" TEXT,
    "endDate" TEXT,
    "startDate_min" TEXT,
    "startDate_max" TEXT,
    "endDate_min" TEXT,
    "endDate_max" TEXT,
    "location" TEXT,
    "observation_source" TEXT,
    "location_in_observation_source" TEXT,
    "reconstruction_source" TEXT,
    "location_in_reconstruction_source" TEXT,
    "comment" TEXT,

    FOREIGN KEY("URI") REFERENCES "persons"("URI")
);

-- This table records observations of identities associated with a specific person
CREATE TABLE IF NOT EXISTS "identities" (
        "id" INTEGER PRIMARY KEY AUTOINCREMENT,
        "URI" TEXT,
        "observation_id" TEXT,
        "reconstruction_id" TEXT,
        "original_label" TEXT,
        "identity" TEXT,
        "identityType" TEXT,
        "location" TEXT,
        "annotationDate" TEXT,
        "startDate" TEXT,
        "endDate" TEXT,
        "startDate_min" TEXT,
        "startDate_max" TEXT,
        "endDate_min" TEXT,
        "endDate_max" TEXT,
        "observation_source" TEXT,
        "location_in_observation_source" TEXT,
        "reconstruction_source" TEXT,
        "location_in_reconstruction_source" TEXT,
        "comment" TEXT,

        FOREIGN KEY("URI") REFERENCES "persons"("URI")
    );

-- This table records observations of statuses associated with a specific person
CREATE TABLE IF NOT EXISTS "statuses" (
        "id" INTEGER PRIMARY KEY AUTOINCREMENT,
        "URI" TEXT,
        "observation_id" TEXT,
        "reconstruction_id" TEXT,
        "original_label" TEXT,
        "status" TEXT,
        "statusType" TEXT,
        "location" TEXT,
        "annotationDate" TEXT,
        "startDate" TEXT,
        "endDate" TEXT,
        "startDate_min" TEXT,
        "startDate_max" TEXT,
        "endDate_min" TEXT,
        "endDate_max" TEXT,
        "observation_source" TEXT,
        "location_in_observation_source" TEXT,
        "reconstruction_source" TEXT,
        "location_in_reconstruction_source" TEXT,
        "comment" TEXT,

        FOREIGN KEY("URI") REFERENCES "persons"("URI")
    );

-- This table records observations of locationRelations associated with a specific person
CREATE TABLE IF NOT EXISTS "locationRelations" (
        "id" INTEGER PRIMARY KEY AUTOINCREMENT,
        "URI" TEXT,
        "observation_id" TEXT,
        "reconstruction_id" TEXT,
        "original_label" TEXT,
        "locationRelation" TEXT,
        "location" TEXT,
        "annotationDate" TEXT,
        "startDate" TEXT,
        "endDate" TEXT,
        "startDate_min" TEXT,
        "startDate_max" TEXT,
        "endDate_min" TEXT,
        "endDate_max" TEXT,
        "observation_source" TEXT,
        "location_in_observation_source" TEXT,
        "reconstruction_source" TEXT,
        "location_in_reconstruction_source" TEXT,
        "comment" TEXT,

        FOREIGN KEY("URI") REFERENCES "persons"("URI")
    );

-- This table records observations of relations between two people in the dataset
CREATE TABLE IF NOT EXISTS "relations" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT,
    "URI" TEXT,
    "observation_id" TEXT,
    "reconstruction_id" TEXT,
    "original_label" TEXT,
    "relation" TEXT,
    "otherPerson" TEXT,
    "annotationDate" TEXT,
    "startDate" TEXT,
    "endDate" TEXT,
    "startDate_min" TEXT,
    "startDate_max" TEXT,
    "endDate_min" TEXT,
    "endDate_max" TEXT,
    "observation_source" TEXT,
    "location_in_observation_source" TEXT,
    "reconstruction_source" TEXT,
    "location_in_reconstruction_source" TEXT,
    "comment" TEXT,

    FOREIGN KEY("URI") REFERENCES "persons"("URI")
);

-- This table records observations of events that a person was involved with (currently exclusively birth and date).
CREATE TABLE IF NOT EXISTS "events" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT,
    "URI" TEXT,
    "observation_id" TEXT,
    "reconstruction_id" TEXT,
    "original_label" TEXT,
    "event" TEXT,
    "argument" TEXT,
    "annotationDate" TEXT,
    "startDate" TEXT,
    "endDate" TEXT,
    "startDate_min" TEXT,
    "startDate_max" TEXT,
    "endDate_min" TEXT,
    "endDate_max" TEXT,
    "observation_source" TEXT,
    "location_in_observation_source" TEXT,
    "reconstruction_source" TEXT,
    "location_in_reconstruction_source" TEXT,
    "comment" TEXT,

    FOREIGN KEY("URI") REFERENCES "persons"("URI")
);

-- this table records other databases identifiers for the same person
CREATE TABLE IF NOT EXISTS "externalReferences" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT,
    "URI" TEXT,
    "reconstruction_id" TEXT,
    "external_db_name" TEXT,
    "external_id" TEXT,
    "external_id_type" TEXT, -- eg. URI, ID etc.

    FOREIGN KEY("URI") REFERENCES "persons"("URI")
);

CREATE TABLE IF NOT EXISTS "reconstructionSources" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT,
    "Zotero_URI" TEXT,
    "geographical_scope" TEXT,
    "temporal_scope_start",
    "temporal_scope_end",
    "creation_period_start" TEXT,
    "creation_period_end" TEXT,
    "external_id_type" TEXT,
    "comment" TEXT
);

CREATE VIEW activeAs_with_ranges AS
SELECT
    id,
    URI,
    observation_id,
    reconstruction_id,
    original_label,
    activity,
    activityType,
    employer,
    location,
    annotationDate,
    observation_source,
    location_in_observation_source,
    reconstruction_source,
    location_in_reconstruction_source,
    comment,
    COALESCE(startDate, startDate_min) AS effectiveStartDate,
    COALESCE(endDate, endDate_max) AS effectiveEndDate
FROM activeAs;

CREATE VIEW appellations_with_ranges AS
SELECT
    id,
    URI,
    observation_id,
    reconstruction_id,
    appellation,
    appellationType,
    annotationDate,
    location,
    observation_source,
    location_in_observation_source,
    reconstruction_source,
    location_in_reconstruction_source,
    comment,
    COALESCE(startDate, startDate_min) AS effectiveStartDate,
    COALESCE(endDate, endDate_max) AS effectiveEndDate
FROM appellations;

CREATE VIEW identities_with_ranges AS
SELECT
    id,
    URI,
    observation_id,
    reconstruction_id,
    original_label,
    identity,
    identityType,
    location,
    annotationDate,
    observation_source,
    location_in_observation_source,
    reconstruction_source,
    location_in_reconstruction_source,
    comment,
    COALESCE(startDate, startDate_min) AS effectiveStartDate,
    COALESCE(endDate, endDate_max) AS effectiveEndDate
FROM identities;

CREATE VIEW statuses_with_ranges AS
SELECT
    id,
    URI,
    observation_id,
    reconstruction_id,
    original_label,
    status,
    statusType,
    location,
    annotationDate,
    observation_source,
    location_in_observation_source,
    reconstruction_source,
    location_in_reconstruction_source,
    comment,
    COALESCE(startDate, startDate_min) AS effectiveStartDate,
    COALESCE(endDate, endDate_max) AS effectiveEndDate
FROM statuses;

CREATE VIEW locationRelations_with_ranges AS
SELECT
    id,
    URI,
    observation_id,
    reconstruction_id,
    original_label,
    locationRelation,
    location,
    annotationDate,
    observation_source,
    location_in_observation_source,
    reconstruction_source,
    location_in_reconstruction_source,
    comment,
    COALESCE(startDate, startDate_min) AS effectiveStartDate,
    COALESCE(endDate, endDate_max) AS effectiveEndDate
FROM locationRelations;

CREATE VIEW relations_with_ranges AS
SELECT
    id,
    URI,
    observation_id,
    reconstruction_id,
    original_label,
    relation,
    otherPerson,
    annotationDate,
    observation_source,
    location_in_observation_source,
    reconstruction_source,
    location_in_reconstruction_source,
    comment,
    COALESCE(startDate, startDate_min) AS effectiveStartDate,
    COALESCE(endDate, endDate_max) AS effectiveEndDate
FROM relations;

CREATE VIEW events_with_ranges AS
SELECT
    id,
    URI,
    observation_id,
    reconstruction_id,
    original_label,
    event,
    argument,
    annotationDate,
    observation_source,
    location_in_observation_source,
    reconstruction_source,
    location_in_reconstruction_source,
    comment,
    COALESCE(startDate, startDate_min) AS effectiveStartDate,
    COALESCE(endDate, endDate_max) AS effectiveEndDate
FROM events;



