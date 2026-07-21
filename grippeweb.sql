-- Seed script for a GrippeWeb MSSQL test database.
-- Creates the GrippeWeb database, the MEx schema and its tables, then inserts
-- the rows used by the MEx GrippeWeb extractor integration tests.
-- The script is idempotent: it can be re-applied to an existing database.

IF DB_ID('GrippeWeb') IS NULL
    CREATE DATABASE GrippeWeb;
GO

USE GrippeWeb;
GO

IF SCHEMA_ID('MEx') IS NULL
    EXEC('CREATE SCHEMA MEx');
GO

DROP TABLE IF EXISTS MEx.vActualQuestion;
DROP TABLE IF EXISTS MEx.vWeeklyResponsesMEx;
DROP TABLE IF EXISTS MEx.vMasterDataMEx;
GO

CREATE TABLE MEx.vActualQuestion (
    Id NVARCHAR(255) NULL,
    StartedOn DATETIME2 NULL,
    FinishedOn DATETIME2 NULL,
    RepeatAfterDays NVARCHAR(255) NULL
);
GO

CREATE TABLE MEx.vWeeklyResponsesMEx (
    GuidTeilnehmer NVARCHAR(255) NULL,
    Haushalt_Registrierer NVARCHAR(255) NULL
);
GO

CREATE TABLE MEx.vMasterDataMEx (
    GuidTeilnehmer NVARCHAR(255) NULL,
    Haushalt_Registrierer NVARCHAR(255) NULL
);
GO

INSERT INTO MEx.vActualQuestion (Id, StartedOn, FinishedOn, RepeatAfterDays)
VALUES
    ('AAA', '2023-11-01 00:00:00.0000000', '2023-12-01 00:00:00.0000000', '1'),
    ('BBB', '2023-12-01 00:00:00.0000000', '2024-01-01 00:00:00.0000000', '2');
GO

INSERT INTO MEx.vWeeklyResponsesMEx (GuidTeilnehmer, Haushalt_Registrierer)
VALUES
    (NULL, NULL),
    (NULL, NULL);
GO

INSERT INTO MEx.vMasterDataMEx (GuidTeilnehmer, Haushalt_Registrierer)
VALUES
    (NULL, NULL),
    (NULL, NULL);
GO
