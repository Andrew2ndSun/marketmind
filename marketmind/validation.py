"""Reject citations that do not refer to supplied evidence."""

def validate_citations(result, evidence):
    valid = {item["id"] for item in evidence}
    claims = [result.summary, *result.findings, *result.conflicting_evidence, *result.risks]
    if any(not set(claim.evidence_ids) <= valid for claim in claims):
        raise ValueError("Model cited evidence that was not supplied.")
