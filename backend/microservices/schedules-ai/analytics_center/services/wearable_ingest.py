"""Wearable ingestion service functions.

Responsibilities:
- Parse uploaded CSV/JSON into raw rows.
- Apply user column mapping.
- Extract sleep + activity features.
- Return structured ingestion result.
"""
from __future__ import annotations
import csv, json, io
import sys
import os
from typing import Dict, List, Any, Optional

# Add analytics_center to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from models.wearable import WearableMapping, WearableRawRecord, ExtractedFeatures, WearableIngestionResult
from utils.validation import to_minutes
import csv, json, io
from typing import List, Dict, Any
from models.wearable import WearableMapping, WearableRawRecord, ExtractedFeatures, WearableIngestionResult
from utils.validation import to_minutes

_DEF_DAY = 1440

def parse_uploaded_file(name: str, content: bytes) -> List[WearableRawRecord]:
    if name.lower().endswith('.csv'):
        text = content.decode('utf-8', errors='ignore')
        reader = csv.DictReader(io.StringIO(text))
        return [WearableRawRecord(data=row) for row in reader]
    if name.lower().endswith('.json'):
        payload = json.loads(content.decode('utf-8', errors='ignore'))
        if isinstance(payload, list):
            return [WearableRawRecord(data=r) for r in payload if isinstance(r, dict)]
        if isinstance(payload, dict):
            return [WearableRawRecord(data=payload)]
    return []

def _extract_sleep(records: List[WearableRawRecord], m: WearableMapping) -> Dict[str, Any]:
    best = None
    note = None
    for r in records:
        sd = m.sleep_start and r.data.get(m.sleep_start)
        ed = m.sleep_end and r.data.get(m.sleep_end)
        if sd and ed:
            best = (sd, ed)
            break
    if not best:
        return {"total_sleep_minutes": None, "main_sleep_window": None, "note": "No sleep window"}
    sd, ed = best
    try:
        smin = to_minutes(sd)
        emin = to_minutes(ed)
        if emin <= smin:
            emin += _DEF_DAY
        dur = emin - smin
        if dur > _DEF_DAY:
            dur = dur % _DEF_DAY
        return {
            "total_sleep_minutes": dur,
            "main_sleep_window": f"{sd}-{ed}",
            "note": None
        }
    except Exception:
        return {"total_sleep_minutes": None, "main_sleep_window": None, "note": "Parse error"}

def _extract_activity(records: List[WearableRawRecord], m: WearableMapping) -> List[Dict[str, Any]]:
    blocks: List[Dict[str, Any]] = []
    for r in records:
        st = m.activity_start and r.data.get(m.activity_start)
        et = m.activity_end and r.data.get(m.activity_end)
        at = m.activity_type and r.data.get(m.activity_type)
        if st and et:
            try:
                dur = to_minutes(et) - to_minutes(st)
                if dur <= 0:
                    continue
                blocks.append({"start": st, "end": et, "type": at or "activity", "duration": dur})
            except Exception:
                continue
    return blocks

def extract_features(records: List[WearableRawRecord], mapping: WearableMapping) -> ExtractedFeatures:
    sleep_info = _extract_sleep(records, mapping)
    activity_blocks = _extract_activity(records, mapping)
    # Simple aggregates
    steps_total = 0
    readiness = None
    stress = None
    sleep_quality = None
    for r in records:
        if mapping.steps and isinstance(r.data.get(mapping.steps), (int, float)):
            steps_total += int(r.data.get(mapping.steps))
        if mapping.readiness_score and readiness is None:
            val = r.data.get(mapping.readiness_score)
            if isinstance(val, (int, float)):
                readiness = float(val)
        if mapping.stress_level and stress is None:
            stress = r.data.get(mapping.stress_level)
        if mapping.sleep_quality and sleep_quality is None:
            sleep_quality = r.data.get(mapping.sleep_quality)
    return ExtractedFeatures(
        total_sleep_minutes=sleep_info.get("total_sleep_minutes"),
        main_sleep_window=sleep_info.get("main_sleep_window"),
        sleep_quality=sleep_quality,
        readiness_score=readiness,
        stress_level=stress,
        steps_total=steps_total or None,
        activity_blocks=activity_blocks,
    )

def ingest_wearable(name: str, content: bytes, mapping: WearableMapping) -> WearableIngestionResult:
    records = parse_uploaded_file(name, content)
    feats = extract_features(records, mapping)
    notes = []
    if feats.total_sleep_minutes is None:
        notes.append("Missing sleep window")
    if feats.readiness_score is not None and not (0 <= feats.readiness_score <= 1):
        notes.append("Readiness score outside 0..1 (raw value kept)")
    return WearableIngestionResult(
        features=feats,
        mapping_used=mapping,
        raw_count=len(records),
        notes=notes,
    )
