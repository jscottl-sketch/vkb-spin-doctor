import pathlib, re, shutil, datetime
f = pathlib.Path('C:/Users/jscot/OneDrive/Desktop/VKB-SpinDoctor/PROJECT_HANDOVER.md')
c = f.read_text(encoding='utf-8')
ts = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
bak = pathlib.Path('C:/Users/jscot/OneDrive/Desktop/VKB-SpinDoctor/backups')
bak.mkdir(exist_ok=True)
import shutil
shutil.copy2(f, bak / ('PROJECT_HANDOVER_before_ed_update_' + ts + '.md'))
print('Backup done')
c = c.replace('| ED Bind Reset prevention | \u23f8 v0.2 |', '| ED Bind Reset prevention | \u2705 Built as problems/ed_bind_reset.py, wired into GUI Fix Mouse Spin tab |')
c = c.replace('**Status:** ACP v1 built. GUI 3 tabs confirmed working. sfl_agent.py v3 (575 lines). Conductor module live.', '**Status:** ACP v1 built. GUI 3 tabs confirmed working. sfl_agent.py v3 (575 lines). Conductor module live. ED Bind Reset prevention built.')
c = re.sub(r'\*\*Last updated:\*\* .*', '**Last updated:** 13 May 2026 (ED bind reset done)', c)
idx = c.find('## NEXT PRIORITIES')
if idx >= 0:
    end = c.find('\n---', idx)
    new_section = '''## NEXT PRIORITIES
\n| # | Task | Tool |
\|---|---|---|
\| 1 | Wire Conductor recommendations into GUI | Claude Code |
\| 2 | win_hardener module (9 problems) | Claude Code |\| 3 | Star Citizen full support | Claude Code |\| 4 | LM Studio local AI wired in (Gemma 4) | Claude Code |\n'''
    c = c[:idx] + new_section + c[end:]
    print('Priorities updated')
else:
    print('WARNING: NEXT PRIORITIES section not found')
f.write_text(c, encoding='utf-8')
print('Done')

