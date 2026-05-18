@echo off
cd /d "%~dp0"
echo ============================================================
echo  AAFL Doctor  --  Pre-flight Health Check
echo ============================================================
python -c "from pathlib import Path; exit(0 if Path('data/knowledge_engine.db').exists() else 1)"
if errorlevel 1 (
    echo  DB         : NOT FOUND at data/knowledge_engine.db
    goto :show_goal
)
python -c "import sqlite3,json;conn=sqlite3.connect('data/knowledge_engine.db');conn.row_factory=sqlite3.Row;row=conn.execute('SELECT quality_score,created_at,metadata FROM knowledge ORDER BY created_at DESC LIMIT 1').fetchone();meta=json.loads(row['metadata'] or '{}') if row else {};score_str=str(row['quality_score'])+'/10  ('+str(row['created_at'])[:16]+')' if row else '(no entries yet)';plan_prov=meta.get('plan_provider','?');work_prov=meta.get('work_provider','?');print('  Score    : '+score_str);print('  Providers: plan='+plan_prov+'  work='+work_prov);c1=conn.execute('SELECT COUNT(*) FROM knowledge').fetchone()[0];c2=conn.execute('SELECT COUNT(*) FROM solution_log').fetchone()[0];print('  DB rows  : knowledge='+str(c1)+'  solution_log='+str(c2));conn.close()"

:show_goal
echo ============================================================
echo  Current Goal:
echo ============================================================
type goal.txt
echo.
echo ============================================================
