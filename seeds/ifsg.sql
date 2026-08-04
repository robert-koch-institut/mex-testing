IF DB_ID('SurvNet3Meta') IS NULL
    CREATE DATABASE SurvNet3Meta;
GO

USE SurvNet3Meta;
GO

IF SCHEMA_ID('Meta') IS NULL
    EXEC('CREATE SCHEMA Meta');
GO

DROP TABLE IF EXISTS Meta.Catalogue2Item;
DROP TABLE IF EXISTS Meta.Catalogue2Item2Schema;
DROP TABLE IF EXISTS Meta.DataType;
DROP TABLE IF EXISTS Meta.Disease;
DROP TABLE IF EXISTS Meta.Field;
DROP TABLE IF EXISTS Meta.Item;
DROP TABLE IF EXISTS Meta.Schema2Field;
DROP TABLE IF EXISTS Meta.Schema2Type;
DROP TABLE IF EXISTS Meta.Type;
GO

CREATE TABLE Meta.Catalogue2Item (
    IdItem INT NULL,
    IdCatalogue INT NULL,
    IdCatalogue2Item INT NULL
);
GO

CREATE TABLE Meta.Catalogue2Item2Schema (
    IdCatalogue2Item INT NULL
);
GO

CREATE TABLE Meta.DataType (
    IdDataType INT NULL,
    DataTypeName NVARCHAR(255) NULL
);
GO

CREATE TABLE Meta.Disease (
    ICD10Code NVARCHAR(255) NULL,
    IdType INT NULL,
    IdSchema INT NULL,
    ReferenceDefA BIT NULL,
    ReferenceDefB BIT NULL,
    ReferenceDefC BIT NULL,
    ReferenceDefD BIT NULL,
    ReferenceDefE BIT NULL,
    IfSGBundesland BIT NULL,
    InBundesland NVARCHAR(255) NULL,
    DiseaseName NVARCHAR(255) NULL,
    DiseaseNameEN NVARCHAR(255) NULL,
    SpecimenName NVARCHAR(255) NULL
);
GO

CREATE TABLE Meta.Field (
    GuiText NVARCHAR(255) NULL,
    GuiTooltip NVARCHAR(255) NULL,
    IdCatalogue INT NULL,
    IdType INT NULL,
    IdDataType INT NULL,
    IdField INT NULL,
    IdFieldType INT NULL,
    ToTransport INT NULL,
    Sort INT NULL,
    StatementAreaGroup NVARCHAR(255) NULL
);
GO

CREATE TABLE Meta.Item (
    ItemName NVARCHAR(255) NULL,
    ItemNameEN NVARCHAR(255) NULL,
    IdItem INT NULL
);
GO

CREATE TABLE Meta.Schema2Field (
    IdSchema INT NULL,
    IdField INT NULL
);
GO

CREATE TABLE Meta.Schema2Type (
    IdSchema INT NULL,
    IdType INT NULL
);
GO

CREATE TABLE Meta.Type (
    Code NVARCHAR(255) NULL,
    IdType INT NULL,
    SqlTableName NVARCHAR(255) NULL
);
GO

INSERT INTO Meta.Catalogue2Item (IdItem, IdCatalogue, IdCatalogue2Item)
VALUES
    (0, 0, 0),
    (1001, 1001, 1);
GO

INSERT INTO Meta.Catalogue2Item2Schema (IdCatalogue2Item)
VALUES
    (1),
    (1);
GO

INSERT INTO Meta.DataType (IdDataType, DataTypeName)
VALUES
    (0, 'DummyType');
GO

INSERT INTO Meta.Disease (
    ICD10Code, IdType, IdSchema,
    ReferenceDefA, ReferenceDefB, ReferenceDefC, ReferenceDefD, ReferenceDefE,
    IfSGBundesland, InBundesland, DiseaseName, DiseaseNameEN, SpecimenName
)
VALUES
    ('A1', 101, 1, 0, 1, 1, 0, 0, 0,
     '01,02,03,04,05,06,07,08,09,10,11,12,13,14,15,16', 'virus', 'Epidemic', 'virus'),
    ('A1', 101, 1, 0, 1, 1, 0, 0, 0,
     '01,02,03,04,05,06,07,08,09,10,11,12,13,14,15,16', 'virus', 'Epidemic', 'virus');
GO

INSERT INTO Meta.Field (
    GuiText, GuiTooltip, IdCatalogue, IdType, IdDataType,
    IdField, IdFieldType, ToTransport, Sort, StatementAreaGroup
)
VALUES
    ('---', NULL, 0, 0, 0, -1, 0, 0, -1, NULL),
    ('---', NULL, 0, 0, 0, 0, 0, 0, 0, NULL);
GO

INSERT INTO Meta.Item (ItemName, ItemNameEN, IdItem)
VALUES
    ('NullItem', NULL, 0),
    ('-nicht erhoben-', '- not enquired -', 1001);
GO

INSERT INTO Meta.Schema2Field (IdSchema, IdField)
VALUES
    (10, 1),
    (10, 2);
GO

INSERT INTO Meta.Schema2Type (IdSchema, IdType)
VALUES
    (1, 0),
    (1, 11);
GO

INSERT INTO Meta.Type (Code, IdType, SqlTableName)
VALUES
    ('test1', 101, 'Disease71ABC'),
    ('test2', 1, 'Disease');
GO
