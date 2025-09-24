# Response models for structured AI output
from typing import List, Optional
from pydantic import BaseModel, Field


class DbtSuggestion(BaseModel):
    """A single dbt model improvement suggestion"""
    suggestion: str = Field(..., description="The improvement suggestion text")
    priority: str = Field(default="medium", description="Priority level: low, medium, high")
    category: str = Field(default="general", description="Category: syntax, performance, best_practice, structure")


class DbtModelSuggestions(BaseModel):
    """Collection of suggestions for a dbt model"""
    model_name: str = Field(..., description="Name of the dbt model")
    suggestions: List[DbtSuggestion] = Field(default_factory=list, description="List of improvement suggestions")
    overall_assessment: Optional[str] = Field(None, description="Overall assessment of the model")
    has_recommendations: bool = Field(True, description="Whether there are any recommendations")


class DbtModelDefinition(BaseModel):
    """Definition for a generated dbt model"""
    model_name: str = Field(..., description="Name of the model")
    sql_content: str = Field(..., description="SQL content of the model")
    description: Optional[str] = Field(None, description="Description of what the model does")
    depends_on: List[str] = Field(default_factory=list, description="List of models this depends on")


class DbtModelsResponse(BaseModel):
    """Response containing multiple generated dbt models"""
    models: List[DbtModelDefinition] = Field(..., description="List of generated models")
    summary: Optional[str] = Field(None, description="Summary of the generated models")