import csv, sqlite3
import pandas
import os

#this is broken or at least very unreliable because the column types are not very well specified from a csv alone
conn = sqlite3.connect("openrussian_csv.db")


dir = "openrussian-csvs"
for filename in os.listdir(dir):
    with open(os.path.join(dir, filename), "r", encoding="utf-8") as f:
        df = pandas.read_csv(f, encoding="utf-8")
        table_name = filename[11:-4]
        print(table_name)
        df.to_sql(table_name, conn, if_exists='replace', index=False)