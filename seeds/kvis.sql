IF DB_ID('KVIS') IS NULL
    CREATE DATABASE KVIS;
GO

USE KVIS;
GO

IF SCHEMA_ID('Mex') IS NULL
    EXEC('CREATE SCHEMA Mex');
GO

DROP TABLE IF EXISTS Mex.vKVISVariables;
DROP TABLE IF EXISTS Mex.vKVISFieldValues;
GO

CREATE TABLE Mex.vKVISVariables (
    FileType NVARCHAR(255) NULL,
    DatatypeDescription NVARCHAR(255) NULL,
    FieldDescription NVARCHAR(255) NULL,
    FieldNameShort NVARCHAR(255) NULL,
    FieldNameLong NVARCHAR(255) NULL,
    FVListName NVARCHAR(255) NULL
);
GO

CREATE TABLE Mex.vKVISFieldValues (
    FieldValueListName NVARCHAR(255) NULL,
    FieldValue NVARCHAR(255) NULL,
    FieldValueLongText NVARCHAR(255) NULL
);
GO

INSERT INTO Mex.vKVISVariables (
    FileType, DatatypeDescription, FieldDescription, FieldNameShort, FieldNameLong, FVListName
)
VALUES
    ('file with integers', 'integer field', 'some integer field', 'int', 'Integer', NULL),
    ('file with strings and bools', 'string field', 'some text field', 'str', 'string', 'STRING'),
    ('file with strings and bools', 'bool field', 'a boolean field for flagging', 'bool', 'boolean', 'BOOL');
GO

INSERT INTO Mex.vKVISFieldValues (FieldValueListName, FieldValue, FieldValueLongText)
VALUES
    ('STRING', 'one', 'the number one'),
    ('STRING', 'two', 'the number two'),
    ('STRING', 'three', 'the number three'),
    ('BOOL', '0', 'it is false'),
    ('BOOL', '1', 'it is true');
GO
