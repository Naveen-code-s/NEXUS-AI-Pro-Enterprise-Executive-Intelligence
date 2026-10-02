from pathlib import Path
import uuid
def generate(settings,title,answer,sources,evidence):
    Path(settings.report_dir).mkdir(parents=True,exist_ok=True); safe=''.join(c if c.isalnum() or c in ' _-' else '_' for c in title)[:70]; p=Path(settings.report_dir)/(safe+'_'+uuid.uuid4().hex[:6]+'.md')
    refs='\n'.join('- '+str(s.get('title','Not available'))+' | '+str(s.get('url') or s.get('doi') or 'Not available') for s in sources) or '- References not available'
    ev='\n'.join('- '+e['level']+': '+e['reason'] for e in evidence) or '- Evidence not available'
    text=f'# {title}\n\n## Executive Summary\n{answer}\n\n## Evidence\n{ev}\n\n## References\n{refs}\n\n## Limitations\nOnly retrieved evidence is represented; unavailable metadata is not inferred.\n'
    p.write_text(text,encoding='utf-8'); return str(p)
