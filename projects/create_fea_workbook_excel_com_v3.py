
"""
FEA Excel Automation (v3)

Uses Microsoft Excel as the calculation engine.

Requirements:
    py -m pip install pywin32 pandas openpyxl

Place beside:
    - convex hull gg plot values.xlsx
    - 2026 Suspension Forces (V2) (1).xlsm
"""

from pathlib import Path
import time
import pandas as pd
import win32com.client as win32
from openpyxl import Workbook

SCALE = 1.15

BASE = Path(__file__).resolve().parent
SOURCE = BASE / "convex hull gg plot values.xlsx"
CALCULATOR = BASE / "2026 Suspension Forces (V2) (1).xlsm"

SHEET = "OUTSIDE FRONT (84.12)"

INPUT_ROW = 98
OUTPUT_ROW = 115

LAT_COL = 3
LONG_COL = 4

# diagnostic outputs
FZFL_COL = 8
FYTOTAL_COL = 10
FXTOTAL_COL = 13

# suspension outputs F:K
SUSP_COLS = [6,7,8,9,10,11]

OUTFILE = BASE / "FEA_Output_Summary_v3.xlsx"

def wait_calc(excel, timeout=10):
    start=time.time()
    while True:
        try:
            if excel.CalculationState == 0:
                return
        except Exception:
            return
        if time.time()-start>timeout:
            raise TimeoutError("Excel calculation timeout")
        time.sleep(0.05)

def main():
    src=pd.read_excel(SOURCE).iloc[:28].copy()

    excel=win32.DispatchEx("Excel.Application")
    excel.Visible=False
    excel.DisplayAlerts=False

    wb=excel.Workbooks.Open(str(CALCULATOR.resolve()))
    ws=wb.Worksheets(SHEET)

    rows=[]

    try:
        for i, (_, r) in enumerate(src.iterrows(), start=1):
            lat=float(r["Fy interp"])*SCALE
            lon=float(r["Fx interp"])*SCALE           
            print(f"\nCase {i}/28")
            print(f"Load case : {r['Load Case']}")
            print(f"Lat G     : {lat:.4f}")
            print(f"Long G    : {lon:.4f}")


            ws.Cells(INPUT_ROW,LAT_COL).Value=lat
            ws.Cells(INPUT_ROW,LONG_COL).Value=lon

            wb.RefreshAll()
            excel.CalculateFullRebuild()
            print("Calculation state:", excel.CalculationState)
            wait_calc(excel)
            print("Finished calculating.")
            time.sleep(0.1)

            fzfl=ws.Cells(INPUT_ROW,FZFL_COL).Value
            fyt=ws.Cells(INPUT_ROW,FYTOTAL_COL).Value
            fxt=ws.Cells(INPUT_ROW,FXTOTAL_COL).Value

            try:
                susp = [ws.Cells(OUTPUT_ROW, c).Value for c in SUSP_COLS]
            except Exception as e:
                print("FAILED:", r["Load Case"])
                print(e)
                print("Output row 115 values:")
                for c in range(6, 12):
                    print(c, ws.Cells(115, c).Value)
                susp = [None] * 6
            print("Fz FL =", fzfl)
            print("Fy Total =", fyt)
            print("Fx Total =", fxt)
            print("Suspension =", susp)            
            rows.append([
                r.iloc[0],
                r["Load Case"],
                r["Fy interp"],
                r["Fx interp"],
                r["Fz interp"],
                lat,
                lon,
                fzfl,
                fyt,
                fxt,
                *susp
            ])
    finally:
        wb.Close(False)
        excel.Quit()

    headers=[
        "Point","Load Case",
        "Source Fy","Source Fx","Source Fz",
        "Scaled Lat G","Scaled Long G",
        "Fz FL","Fy Total","Fx Total",
        "Up-Fore","Up-Aft","Low-Fore","Low-Aft","Push/Pull","Tie/Toe"
    ]

    outwb=Workbook()
    wsout=outwb.active
    wsout.title="FEA_Output_Summary"
    wsout.append(headers)
    for r in rows:
        wsout.append(r)
    outwb.save(OUTFILE)

    print("Finished")
    print(OUTFILE)

if __name__=="__main__":
    main()
