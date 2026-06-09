# Day 1 Notes

## Completed

- Created GitHub repository
- Added README
- Added study protocol
- Added data inventory
- Created local project folder in VS Code
- Connected local project folder to GitHub
- Added `.gitignore` to prevent raw data from being committed
- Downloaded Massachusetts municipal boundaries from MassGIS
- Extracted shapefile locally into `data/raw/massgis_municipalities/`
- Downloaded Massachusetts opioid-related overdose deaths by city/town report
- Confirmed overdose deaths file contains data from 2016–2023
- Documented decision to use 2021–2023 average fatal overdose burden for MVP
- Downloaded Massachusetts opioid-related EMS incidents report
- Confirmed EMS report contains suspected opioid-related incidents by town for 2022–2023
- Documented EMS incidents as an emergency opioid-related burden indicator, not a strictly nonfatal overdose measure
- Found Mass.gov Harm Reduction Program Locator
- Found Mass.gov Syringe Service Program Locator
- Found Mass.gov Peer Recovery Support Centers list
- Found BSAS dashboard as a contextual source
- Exported SAMHSA FindTreatment.gov Massachusetts treatment facility data
- Downloaded SAMHSA CSV and Excel/code reference files
- Downloaded CDC/ATSDR 2022 Massachusetts census tract-level SVI CSV
- Confirmed SVI file contains approximately 1,614 tract rows

## Downloaded Core Datasets

- MassGIS municipal boundaries
- Opioid-related overdose deaths by city/town
- Opioid-related EMS incidents
- SAMHSA Massachusetts treatment facilities
- CDC/ATSDR Social Vulnerability Index

## Found But Not Yet Extracted

- Harm Reduction Program Locator
- Syringe Service Program Locator
- Peer Recovery Support Centers
- BSAS Dashboard

## Next Steps

- Inspect all raw datasets
- Extract tables from overdose and EMS DOCX files
- Clean SAMHSA facility data
- Inspect SVI columns
- Create first processed municipality-level datasets