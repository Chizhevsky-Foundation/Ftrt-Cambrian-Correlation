Cosmic Data

This directory contains raw and processed cosmic data used for the FTRT-Cambrian Correlation Project.
Subdirectories

    raw/: Raw data from external sources (JPL Horizons, GEOMAGIA50, etc.)
    processed/: Processed data ready for analysis

Data Sources

    JPL Horizons: Planetary ephemeris data
    GEOMAGIA50: Paleomagnetic field intensity records
    NOAA: Solar activity data
    NASA: Cosmic ray flux measurements

File Naming Convention

    Raw files: {source}_{dataset}_{date_range}.csv
    Processed files: `{dataset}_{processing_date}.csv

 
data/evolutionary/README.md 
Evolutionary Data

This directory contains raw and processed evolutionary data used for the FTRT-Cambrian Correlation Project.
Subdirectories

    raw/: Raw data from external sources (Paleobiology Database, TimeTree, etc.)
    processed/: Processed data ready for analysis

Data Sources

    Paleobiology Database: Fossil occurrence data
    TimeTree: Molecular divergence times
    Fossilworks: Taxonomic information
    PBDB: Diversity curves and extinction events

File Naming Convention

    Raw files: {source}_{dataset}_{date_range}.csv
    Processed files: `{dataset}_{processing_date}.csv

 
data/processed/README.md 
Processed Data

This directory contains processed data ready for analysis in the FTRT-Cambrian Correlation Project.
Data Types

    FTRT peaks: Planetary alignment events
    Geomagnetic minima: Periods of weakened geomagnetic field
    Speciation events: Evolutionary speciation events
    Extinction events: Evolutionary extinction events
    Correlation results: Results from correlation analyses

File Naming Convention

    `{data_type}{start_date}{end_date}_{processing_date}.csv
