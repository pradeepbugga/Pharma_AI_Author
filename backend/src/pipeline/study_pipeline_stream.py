from backend.src.study_context.model import build_study_model_context
from backend.src.extraction.fields.extract_study_model import extract_model

from backend.src.study_context.admin import build_administration_context
from backend.src.extraction.fields.extract_administration import extract_admin

from backend.src.study_context.dose import build_dose_context
from backend.src.extraction.fields.extract_dose import extract_dose_LLM

from backend.src.study_context.duration import build_duration_context
from backend.src.extraction.fields.extract_duration import extract_duration

from backend.src.study_context.formulation import build_formulation_context
from backend.src.extraction.fields.extract_formulation import extract_formulation

from backend.src.extraction.fields.extract_broad_objectives import extract_objectives

import asyncio

async def run_study_pipeline_stream(primary_drug, sections):
    
    # STUDY MODEL CONTEXT BUILDING AND STUDY MODEL EXTRACTION

    yield {"status": "Extracting study model"}
    await asyncio.sleep(0)
    
    
    study_context = build_study_model_context(primary_drug, " ".join(sections['abstract'] + sections['results']))
    study_result = extract_model(primary_drug, study_context)

    # ADMINISTRATION CONTEXT BUILDING AND EXTRACTION

    yield {"status": "Extracting administration details"}
    await asyncio.sleep(0)

    admin_context = build_administration_context(primary_drug, sections, study_result, study_context)
    administration_result = extract_admin(primary_drug, admin_context["admin_chunks"], admin_context["model_chunks"], study_result)

    # DOSE CONTEXT BUILDING AND EXTRACTION

    yield {"status": "Extracting dose and route"}
    await asyncio.sleep(0)

    in_vivo_dose_candidates, dose_contexts = build_dose_context(primary_drug, sections)
    dose_result = extract_dose_LLM(primary_drug, in_vivo_dose_candidates, dose_contexts, admin_context["admin_chunks"], administration_result)

    # DURATION CONTEXT BUILDING AND EXTRACTION

    yield {"status": "Extracting planned duration"}
    await asyncio.sleep(0)

    duration_context = build_duration_context(sections)
    duration_result = extract_duration(primary_drug, duration_context, admin_context["admin_chunks"], administration_result, dose_result)


    # FORMULATION CONTEXT BUILDING AND EXTRACTION

    yield {"status": "Extracting formulation details"}
    await asyncio.sleep(0)

    formulation_context = build_formulation_context(primary_drug, sections)
    formulation_result = extract_formulation(primary_drug, formulation_context)


    # BROAD OBJECTIVES EXTRACTION

    yield {"status": "Extracting broad objectives"}
    await asyncio.sleep(0)

    broad_objectives = extract_objectives(primary_drug, " ".join(sections['abstract'] + sections['discussion']))
    

    yield {
        "status": "Study pipeline complete",
        "study_model": study_result,
        "administration": administration_result,
        "dose": dose_result,
        "route": dose_result.get("route", "N/A"),
        "duration": duration_result,
        "formulation": formulation_result,
        "broad_objectives": broad_objectives
    }
