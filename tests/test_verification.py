from agents.verification_agent import VerificationAgent
def test_direct_evidence(): assert VerificationAgent().run('retrieval system',[{"source_id":"x","abstract":"retrieval system evaluation"}])[0]["level"]=='Direct evidence'
