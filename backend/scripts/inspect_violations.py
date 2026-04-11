import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()
url = os.environ.get('DATABASE_URL')
print('DATABASE_URL:', url)
if url is None:
    raise SystemExit('DATABASE_URL missing')
engine = create_engine(url.replace('+asyncpg', ''), future=True)
with engine.connect() as conn:
    cols = conn.execute(
        text("SELECT column_name, ordinal_position, data_type FROM information_schema.columns WHERE table_name='violations' ORDER BY ordinal_position")
    ).all()
    print('columns:')
    for c in cols:
        print(c)

    cons = conn.execute(
        text("SELECT conname, pg_get_constraintdef(oid) FROM pg_constraint WHERE conrelid = 'violations'::regclass")
    ).all()
    print('\nconstraints:')
    for c in cons:
        print(c)

    row = conn.execute(text('SELECT * FROM violations LIMIT 1')).first()
    print('\nexample row:')
    print(row)
