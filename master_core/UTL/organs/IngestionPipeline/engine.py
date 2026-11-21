from orchestrator.organ_contract import OrganRequest, OrganResponse


def execute(request: OrganRequest) -> OrganResponse:
	if "records" not in request.payload:
		records = [request.payload]
	else:
		records = request.payload["records"]
		if not isinstance(records, list):
			return OrganResponse(
				success=False,
				data={},
				error="payload.records must be a list of dictionaries.",
			)

	ingested_records: list[dict] = []
	for index, record in enumerate(records):
		if not isinstance(record, dict):
			return OrganResponse(
				success=False,
				data={},
				error=f"payload.records[{index}] must be a dictionary.",
			)
		ingested_records.append(record.copy())

	return OrganResponse(
		success=True,
		data={
			"records": ingested_records,
			"record_count": len(ingested_records),
			"context_tags": request.context_tags.copy(),
		},
	)
