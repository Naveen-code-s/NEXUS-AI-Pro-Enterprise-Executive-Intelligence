from reports.generator import generate
class ReportAgent:
    name="Report"
    def run(self,settings,title,answer,sources,evidence): return generate(settings,title,answer,sources,evidence)
