from typing import List, Literal, Optional
from pydantic import BaseModel, Field, HttpUrl, confloat

# ---- leaf types -------------------------------------------------------------

SubmissionType = Literal["webform", "email", "phone", "mail", "account", "other"]

FieldType = Literal[
    "text", "textarea", "email", "phone", "select", "radio", "checkbox",
    "date", "file", "hidden", "number", "url", "other"
]

RequirementStatus = Literal["required", "optional", "unsure"]
Darkpatternstatus =  Literal["found", "not found"]

class SubmissionMethod(BaseModel):
    type: SubmissionType
    location: str = Field(..., description="page URL or CSS/XPath selector")
    details: Optional[str] = Field(None, description="brief description")

class FormField(BaseModel):
    field_name: str
    type: FieldType
    requirement_status: RequirementStatus

class EvidenceItem(BaseModel):
    page_url: str
    evidence_type: Literal["policy_text","ui_behavior","interaction_obstacle"]
    raw_snippet : Optional[str] = None
    observed_ui_text: Optional[str] = None
    action_taken: Optional[str] = None
    dynamic_outcome: Optional[str] = None

class DarkPatternMatch(BaseModel):
    pattern_name: str                    
    status: Darkpatternstatus # e.g., "found", "not found"
    evidence: List[EvidenceItem] = Field(default_factory=list)
    short_rationale: str
    matching_confidence: confloat(ge=0.0, le=1.0)  # 0–1

class VerificationIssue(BaseModel):
    blocked: bool
    blocker_type: Optional[str] = None        
    blocker_message: Optional[str] = None
    blocked_stage: Optional[str] = None          
    static_html_checked: Optional[bool] = None
    static_html_findings: Optional[str] = None
    details: Optional[str] = None

# ---- top-level output -------------------------------------------------------

class DarkPatternRunResult(BaseModel):
    observed_submission_methods: List[SubmissionMethod] = Field(default_factory=list)
    meets_two_method_requirement: Optional[bool] = None
    form_fields: List[FormField] = Field(default_factory=list)
    dark_patterns_detected: List[DarkPatternMatch] = Field(default_factory=list)
    verification_issue: Optional[VerificationIssue] = None
