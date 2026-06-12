# Day 3 Notes

## Completed

- Created `notebooks/04_build_distance_access_metrics.ipynb`
- Revisited the access measurement approach after identifying that within-municipality service counts were too strict
- Recognized that municipal boundaries do not fully represent real-world recovery access
- Added distance-based recovery access metrics to account for nearby services across municipal borders
- Inspected cleaned service datasets for latitude and longitude availability
- Confirmed exact latitude/longitude was incomplete across service datasets
- Used ZIP-code centroids as approximate service locations for distance calculations
- Fixed ZIP-code formatting issues, including restoring leading zeroes for Massachusetts ZIP codes
- Combined treatment, peer recovery, syringe service, and harm reduction listings into one service dataset
- Created a valid service point dataset using ZIP-code centroid coordinates
- Loaded Massachusetts municipality boundaries
- Created municipality centroid points for distance calculations
- Calculated nearest source-listed recovery service distance for each municipality
- Calculated number of source-listed services within 5 miles
- Calculated number of source-listed services within 10 miles
- Calculated number of service types available within 5 miles
- Calculated number of service types available within 10 miles
- Calculated nearest distance by service category
- Created municipality-level distance access table
- Joined distance access metrics to the final priority index
- Created `nearby_access_coverage_pct`
- Created `distance_adjusted_priority_score`
- Added nearest service access categories
- Saved final priority table with distance metrics
- Created dashboard-ready GeoJSON with distance metrics
- Pushed notebook 4 changes to GitHub
- Created Streamlit dashboard app in `app/streamlit_app.py`
- Added dashboard dependencies using `uv`
- Built dashboard landing page with KPI cards and interactive Massachusetts map
- Added KPI explanations using popovers
- Added Top Communities section
- Added priority bar chart
- Added Access vs Burden scatter plot
- Added Methodology section
- Updated dashboard map to use `Priority Score` as the public-facing label
- Updated map hover labels to use plain-language explanations instead of backend variable names
- Updated dashboard wording to describe services as source-listed records
- Confirmed dashboard runs locally

## Created Processed Outputs

- `municipality_distance_access_metrics.csv`
- `municipality_final_priority_index_with_distance.csv`
- `municipality_final_priority_index_with_distance.geojson`

## Key Methodology Decisions

- Added distance-based access because within-municipality service counts alone can overstate access gaps
- Treated source-listed services in nearby municipalities as relevant to recovery access
- Used ZIP-code centroids as approximate service locations because exact latitude/longitude was incomplete
- Interpreted distance metrics as approximate access measures, not exact travel time or exact address-level distance
- Used municipality centroids as representative points for distance calculations
- Created 5-mile and 10-mile nearby service indicators
- Created a distance-adjusted priority score to reduce overstatement of gaps where nearby services exist
- Continued to describe service counts as source-listed records from SAMHSA and Mass.gov datasets
- Avoided claiming that zero tracked listings means no recovery support exists locally

## Next Steps

- Continue refining the Streamlit dashboard layout and language
- Add sidebar filters for county, priority category, gap category, and nearest service access category
- Rename dashboard table columns for public-facing readability
- Add a clear explanation of the Priority Score
- Add dashboard instructions to the README
- Add screenshots of the dashboard to the project repository
- Write a concise methodology section for the README
- Document project limitations clearly
- Add future improvements section, including exact geocoding, travel-time access, service capacity, and public transit access
- Prepare final portfolio write-up
- Prepare LinkedIn post summarizing the project