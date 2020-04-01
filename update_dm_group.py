import sqlite3
import pandas as pd


db_conn = sqlite3.connect('auto-insta.db')
groups_df = pd.read_excel('insta_config.xlsx', sheet_name='groups')

for idx, group in groups_df.iterrows():
    group_name = group.get('group_name')
    group_code = group.get('group_code')
    group_rules = group.get('group_rules')
    if pd.read_sql(f'select * from dim_group where group_name="{group_name}";', db_conn).empty:
        db_conn.execute(f'''INSERT INTO
            dim_group(group_name,group_code,group_rules) Values
            ("{group_name}","{group_code}","{group_rules}");
        ''')
    else:
        db_conn.execute(f'''UPDATE dim_group
            SET group_rules="{group_rules}", group_code="{group_code}"
            WHERE group_name="{group_name}";
        ''')
db_conn.commit()
