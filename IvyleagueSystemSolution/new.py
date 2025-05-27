import pandas as pd

pprs = pd.read_excel("resource/ivy pricing.xlsx") #$, encoding="utf16")
# pprs.dropna(inplace=True)
# print(pprs.tail())
# print(pprs.columns)
# print(pprs["Knowledge papers"])
# for i, some in pprs.iterrows():
#     f = " Stan"
#     if not isinstance(some["Knowledge papers"], float):
#         print(" ".join(some["Knowledge papers"].split()[:-1])+f, some.Standard, some.revision)
    # break
for i, paper in pprs.iterrows():
    if not isinstance(paper["Knowledge papers"], float):
        if "papers" in paper["Knowledge papers"].lower():
            continue
        variations = [(" Standard", "std"), (" Intensive", "int")]
        for i in range(2):
            code = paper["Knowledge papers"].split()[-1]
            if code in ["BT", "FA", "MA", "CBL", "OBU", "DipIFRS"] and i != 0:
                continue
            if code in ["OBU", "DipIFRS"]:
                revision = 0
                extension = ""
                price = paper.Standard
            else:
                code = "TX" if code == "TAX" else code
                code = f"{code}-{variations[i][1]}"
                extension = variations[i][0]
                price = paper.Standard + paper.revision
                revision = 20_000 if code[-3:] == "std" else 0

            print(
                " ".join(paper["Knowledge papers"].split()[:-1]).title() + extension, "|",
                code, "|",
                int(price), "|",
                revision
            )
# print("performance management".title())
"""Business and Technology BT
1                Management Accounting MA
2                 Financial Accounting FA
5          Corporate and Business Law CBL
6               performance Management PM
7                            Taxation TAX
8                  Financial Reporting FR
9                  Audit and Assurance AA
10                Financial Management FM
13         Strategic Business Leaders SBL
14       Strategic Business Reporting SBR
15      Advanced Financial Management AFM
16    Advanced Performance Management APM
17                  Advanced Taxation ATX
18       Advanced Audit and Assurance AAA"""