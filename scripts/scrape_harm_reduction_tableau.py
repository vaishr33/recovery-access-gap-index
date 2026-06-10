from pathlib import Path
from tableauscraper import TableauScraper as TS

OUT_DIR = Path("data/raw/manual_sources/tableau_harm_reduction_exports")
OUT_DIR.mkdir(parents=True, exist_ok=True)

url = "https://public.tableau.com/views/CNPOENDUpdate_17031806874890/MAHarmReductionPrograms?:embed=y&:showVizHome=no"

print("Loading Tableau view...")
ts = TS()
ts.loads(url)

workbook = ts.getWorkbook()

print("\nWorksheets found:")
for i, ws in enumerate(workbook.worksheets):
    print(f"{i}: {ws.name}")

print("\nSaving worksheet data...")
for i, ws in enumerate(workbook.worksheets):
    try:
        df = ws.data
        safe_name = "".join(c if c.isalnum() or c in " _-" else "_" for c in ws.name).strip()
        out_path = OUT_DIR / f"{i:02d}_{safe_name}.csv"
        df.to_csv(out_path, index=False)
        print(f"{i}: {ws.name} -> {df.shape} -> {out_path}")
    except Exception as e:
        print(f"{i}: {ws.name} -> ERROR: {e}")

print("\nDone.")