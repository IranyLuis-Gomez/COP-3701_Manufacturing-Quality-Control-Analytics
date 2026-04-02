/* Dropping Tables */
DROP TABLE ItemDefect CASCADE CONSTRAINTS;
DROP TABLE Inspection CASCADE CONSTRAINTS;
DROP TABLE Measurement CASCADE CONSTRAINTS;
DROP TABLE QualityPrediction CASCADE CONSTRAINTS;
DROP TABLE ProducedItem CASCADE CONSTRAINTS;
DROP TABLE Defect CASCADE CONSTRAINTS;
DROP TABLE Inspector CASCADE CONSTRAINTS;
DROP TABLE Product CASCADE CONSTRAINTS;
DROP TABLE ProductionLine CASCADE CONSTRAINTS;

/* ProductionLine */
CREATE TABLE ProductionLine (
    LineID NUMBER PRIMARY KEY,
    LineName VARCHAR2(100) UNIQUE,
    Location VARCHAR2(100)
);

/* Product */
CREATE TABLE Product (
    ProductID NUMBER PRIMARY KEY,
    ProductName VARCHAR2(100) UNIQUE,
    Category VARCHAR2(50),
    StdQualityThreshold NUMBER
);

/* ProducedItem */
CREATE TABLE ProducedItem (
    ItemID NUMBER PRIMARY KEY,
    LineID NUMBER,
    ProductID NUMBER,
    ProductionDateTime DATE,
    QualityScore NUMBER,
    BatchNumber VARCHAR2(50),

    FOREIGN KEY (LineID) REFERENCES ProductionLine(LineID),
    FOREIGN KEY (ProductID) REFERENCES Product(ProductID)
);

/* Measurement */
CREATE TABLE Measurement (
    ItemID NUMBER,
    MeasurementNum NUMBER,
    MeasureType VARCHAR2(100),
    MeasureValue NUMBER,
    MeasureDateTime DATE,

    PRIMARY KEY (ItemID, MeasurementNum),
    FOREIGN KEY (ItemID) REFERENCES ProducedItem(ItemID)
);

/* Inspector */
CREATE TABLE Inspector (
    InspectorID NUMBER PRIMARY KEY,
    FName VARCHAR2(50),
    LName VARCHAR2(50),
    CertificationLvl VARCHAR2(100)
);

/* Inspection */
CREATE TABLE Inspection (
    InspectionID NUMBER PRIMARY KEY,
    InspectorID NUMBER,
    ItemID NUMBER,
    InspectionDateTime DATE,
    Result VARCHAR2(10),
    Notes VARCHAR2(255),

    FOREIGN KEY (InspectorID) REFERENCES Inspector(InspectorID),
    FOREIGN KEY (ItemID) REFERENCES ProducedItem(ItemID)
);

/* Defect */
CREATE TABLE Defect (
    DefectID NUMBER PRIMARY KEY,
    DefectName VARCHAR2(100) UNIQUE,
    SeverityLvl NUMBER,
    Description VARCHAR2(255)
);

/* ItemDefect */
CREATE TABLE ItemDefect (
    ItemID NUMBER,
    DefectID NUMBER,
    DefectDateTime DATE,

    PRIMARY KEY (ItemID, DefectID),
    FOREIGN KEY (ItemID) REFERENCES ProducedItem(ItemID),
    FOREIGN KEY (DefectID) REFERENCES Defect(DefectID)
);

/* QualityPrediction */
CREATE TABLE QualityPrediction (
    ItemID NUMBER PRIMARY KEY,
    PredQualityScore NUMBER,
    PredDefectProb NUMBER,
    PredDateTime DATE,
    ConfidenceLvl NUMBER,
    ModelVer VARCHAR2(50),

    FOREIGN KEY (ItemID) REFERENCES ProducedItem(ItemID)
);
