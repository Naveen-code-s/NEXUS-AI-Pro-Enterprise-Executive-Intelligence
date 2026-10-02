from pathlib import Path
from reports.generator import generate
class S: report_dir='/tmp/nexus_test_reports'
def test_report(tmp_path):
    S.report_dir=str(tmp_path); p=generate(S,'Test','Answer',[],[]); assert Path(p).exists()
