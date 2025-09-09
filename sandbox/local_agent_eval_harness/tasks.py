import os, json, glob

# A task describes:
# - pack_glob: glob to locate the pack directory (e.g., *LocalAgentEvalSuite)
# - answer_path: relative path to the pack's answers file
# - answer_key_path: list for drilling into the JSON (e.g., ['finance', 'invoice_to_bank_match'])
# - prompt: the instruction sent to providers; providers should return JSON
# - extractor: function(model_json) -> comparable object (defaults to identity)

def _id(x): return x

TASKS = [
    # Pack 1
    dict(
        name="p1_finance_invoice_match",
        pack_glob="pack1",
        answer_path="answers.json",
        answer_key_path=["finance", "invoice_to_bank_match"],
        prompt="Return JSON with invoice_id, bank_date (YYYY-MM-DD), and amount for Vendor X INV-1043 by reading local files.",
        extractor=_id
    ),
    dict(
        name="p1_hr_post_termination",
        pack_glob="pack1",
        answer_path="answers.json",
        answer_key_path=["hr_security", "post_termination_access"],
        prompt="Return JSON with employee_id, name, and a list of 'timestamp door result' strings for any badge events after termination.",
        extractor=_id
    ),
    dict(
        name="p1_ops_spike",
        pack_glob="pack1",
        answer_path="answers.json",
        answer_key_path=["ops"],
        prompt="Return JSON with keys: 500_spike_window (human-readable), top_endpoint, root_cause_hint by correlating nginx.log and system.log.",
        extractor=_id
    ),

    # Pack 2
    dict(
        name="p2_emails_discount_thread",
        pack_glob="pack2",
        answer_path="answers_pack2.json",
        answer_key_path=["emails", "discount_thread"],
        prompt="Parse emails to return JSON with po, issue_invoice, corrected_invoice, discount, start, skus.",
        extractor=_id
    ),
    dict(
        name="p2_audio_merge",
        pack_glob="pack2",
        answer_path="answers_pack2.json",
        answer_key_path=["audio", "merged_transcript"],
        prompt="Merge transcript segments across silence. Return a list of {start, end, text} segments preserving cluster start times.",
        extractor=_id
    ),
    dict(
        name="p2_finance_fx",
        pack_glob="pack2",
        answer_path="answers_pack2.json",
        answer_key_path=["finance_advanced"],
        prompt="Compute effective USD for EUR 4300 on 2025-06-20 per fx_notes.md and compare vs ledger USD; return JSON with fx_effective_usd and delta_vs_ledger_usd.",
        extractor=lambda x: dict(fx_effective_usd=round(x.get('fx_effective_usd', 0),2), delta_vs_ledger_usd=round(x.get('delta_vs_ledger_usd',0),2))
    ),

    # Pack 3
    dict(
        name="p3_ocr_invoice",
        pack_glob="pack3",
        answer_path="answers_pack3.json",
        answer_key_path=["ocr_scans"],
        prompt="OCR PBM scans to extract inv_id, discount, po, bank_wire_ref, delivery_order and delivery_sku_qty (with date). Return JSON.",
        extractor=_id
    ),
    dict(
        name="p3_sql_recon",
        pack_glob="pack3",
        answer_path="answers_pack3.json",
        answer_key_path=["sql_recon"],
        prompt="From sql/sales.db and archives/audit_bundle.tar (zip inside), compute o2007_unit_price_db, agreed_unit_price_zip, qty, total_difference_usd, refund_recorded_usd, refund_needed_additional_usd. Return JSON.",
        extractor=_id
    ),

    # Pack 4
    dict(
        name="p4_eml_attachments",
        pack_glob="pack4",
        answer_path="answers_pack4.json",
        answer_key_path=["eml_attachments"],
        prompt="Parse inv3001_with_attachments.eml. Return JSON with csv_rows (as list of dicts) and attached_pdf filename.",
        extractor=_id
    ),
    dict(
        name="p4_xlsx_summary",
        pack_glob="pack4",
        answer_path="answers_pack4.json",
        answer_key_path=["xlsx_formulas"],
        prompt="Evaluate ops_finance.xlsx formulas and return JSON with expected_values for Inputs!D2, Inputs!D3, Summary!B1, Summary!B2.",
        extractor=lambda x: x.get('expected_values', x)
    ),
]
