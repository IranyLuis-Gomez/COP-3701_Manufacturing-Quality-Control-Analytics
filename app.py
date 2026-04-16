import oracledb

oracledb.init_oracle_client(lib_dir=r"C:\oracle\instantclient_23_0")

conn = oracledb.connect(
    user="PERACCINY007_SCHEMA_PW850",
    password="DMSE!1CDYT9N64F1rTRG3K75EGRM1I",
    dsn="db.freesql.com:1521/23ai_34ui2"
)

cur = conn.cursor()


# 1. Defect Frequency Analysis
def f1():
    print("\n--- Defect Frequency ---")

    cur.execute("""
        SELECT d.DefectName, COUNT(*)
        FROM ItemDefect id
        JOIN Defect d ON id.DefectID = d.DefectID
        GROUP BY d.DefectName
        ORDER BY COUNT(*) DESC
    """)

    print("DefectName | Count")
    for r in cur:
        print(r[0], r[1])


# 2. Inspector Workload Analysis
def f2():
    print("\n--- Inspector Workload ---")

    inp = input("Inspector ID (blank = all): ")

    if inp == "":
        cur.execute("""
            SELECT i.InspectorID, i.FName, i.LName, COUNT(*)
            FROM Inspection ins
            JOIN Inspector i ON ins.InspectorID = i.InspectorID
            GROUP BY i.InspectorID, i.FName, i.LName
        """)
    else:
        cur.execute("""
            SELECT i.InspectorID, i.FName, i.LName, COUNT(*)
            FROM Inspection ins
            JOIN Inspector i ON ins.InspectorID = i.InspectorID
            WHERE i.InspectorID = :x
            GROUP BY i.InspectorID, i.FName, i.LName
        """, x=inp)

    print("ID | FName | LName | Count")
    for r in cur:
        print(r[0], r[1], r[2], r[3])


# 3. Batch Productivity Ranking
def f3():
    print("\n--- Batch Productivity ---")

    cur.execute("""
        SELECT BatchNumber, COUNT(*)
        FROM ProducedItem
        GROUP BY BatchNumber
        ORDER BY COUNT(*) DESC
    """)

    print("Batch | Total")
    for r in cur:
        print(r[0], r[1])


def f4():
    print("\n--- Line Productivity ---")

    cur.execute("""
        SELECT pl.LineName, COUNT(*)
        FROM ProducedItem pi
        JOIN ProductionLine pl ON pi.LineID = pl.LineID
        GROUP BY pl.LineName
        ORDER BY COUNT(*) DESC
    """)

    rows = cur.fetchall()

    print("There are", len(rows), "lines in the ranking.")

    start = int(input("Start rank: "))
    end = int(input("End rank: "))

    print("Rank | Line | Items")

    rank = start
    for r in rows[start-1:end]:
        print(rank, r[0], r[1])
        rank += 1

# 5. Quality Comparison
def f5():
    print("\n--- Quality Check ---")

    cur.execute("""
        SELECT pi.ItemID, pi.QualityScore, qp.PredQualityScore
        FROM ProducedItem pi
        JOIN QualityPrediction qp ON pi.ItemID = qp.ItemID
    """)

    print("Item | Actual | Pred")
    for r in cur:
        print(r[0], r[1], r[2])


# MENU
while True:
    print("\n1 Defects")
    print("2 Inspectors")
    print("3 Batch")
    print("4 Lines")
    print("5 Quality")
    print("0 Exit")

    c = input(">> ")

    if c == "1":
        f1()
    elif c == "2":
        f2()
    elif c == "3":
        f3()
    elif c == "4":
        f4()
    elif c == "5":
        f5()
    elif c == "0":
        break

cur.close()
conn.close()