from typing import List, Literal, Optional
from pydantic import BaseModel, Field, HttpUrl, confloat

# ---- leaf types -------------------------------------------------------------

SubmissionType = Literal["webform", "email", "phone", "mail", "account", "other"]

FieldType = Literal[
    "text", "textarea", "email", "phone", "select", "radio", "checkbox",
    "date", "file", "hidden", "number", "url", "other"
]

BlockCategory = Literal[
    "security_barrier",
    "automation_instability",
    "interaction_failure",
    "navigation_failure",
    "content_access_limitation",
    "agent_reasoning_failure",
    "unknown",
    "no_blocking"
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
    timing_notes: Optional[str] = None
    example_name: Optional[str] = Field(
        None,
        description=(
            "If the dark pattern was found, specify the example from the taxonomy "
            "that best matches this evidence (e.g., 'Technical Identifier Burden', "
            "'Relationship Gate'). If not found, set to null."
        )
    )

class DarkPatternMatch(BaseModel):
    pattern_name: str                    # the matched issue/DP name
    status: Darkpatternstatus # e.g., "found", "not found"
    evidence: List[EvidenceItem] = Field(default_factory=list)
    short_rationale: str
    matching_confidence: confloat(ge=0.0, le=1.0)  # 0–1

class VerificationIssue(BaseModel):
    blocked: bool
    block_category: BlockCategory
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
