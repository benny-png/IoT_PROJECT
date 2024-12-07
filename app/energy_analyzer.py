# app/energy_analyzer.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
from openai import OpenAI
import json
from datetime import datetime
import os

router = APIRouter()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

class EnergyData(BaseModel):
    data: Dict[str, Any]
    analysis_type: Optional[str] = "general"

def generate_prompt(data: Dict, analysis_type: str) -> str:
    """Generate appropriate prompt based on data and analysis type"""
    
    data_description = json.dumps(data, indent=2)
    
    prompts = {
        "general": f"""
            As an energy analysis expert, analyze this energy consumption data and provide:
            1. Key insights about energy usage patterns
            2. Specific recommendations for energy savings
            3. Potential cost-saving opportunities
            4. Environmental impact insights
            
            Data: {data_description}
            
            Provide recommendations in a structured format with clear, actionable items.
            """,
            
        "savings": f"""
            Focus on cost-saving opportunities in this energy data:
            1. Identify peak usage periods
            2. Calculate potential savings
            3. Suggest specific energy-saving measures
            4. Prioritize recommendations by ROI
            
            Data: {data_description}
            """,
            
        "patterns": f"""
            Analyze energy consumption patterns in this data:
            1. Identify usage trends
            2. Highlight anomalies
            3. Compare with industry standards
            4. Suggest optimization strategies
            
            Data: {data_description}
            """
    }
    
    return prompts.get(analysis_type, prompts["general"])

@router.post("/analyze")
async def analyze_energy_data(request: EnergyData):
    """Analyze energy data and provide recommendations"""
    try:
        # Generate appropriate prompt
        prompt = generate_prompt(request.data, request.analysis_type)
        
        # Get recommendations from OpenAI
        completion = client.chat.completions.create(
            model="gpt-4",  # or use gpt-3.5-turbo for faster, cheaper responses
            messages=[
                {"role": "system", "content": "You are an energy efficiency expert specializing in data analysis and providing actionable recommendations."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,  # Balanced between creativity and consistency
            max_tokens=1000   # Adjust based on needed response length
        )
        
        # Extract and format recommendations
        recommendations = completion.choices[0].message.content
        
        # Add metadata to response
        response = {
            "timestamp": datetime.now().isoformat(),
            "analysis_type": request.analysis_type,
            "recommendations": recommendations,
            "data_summary": {
                "fields_analyzed": list(request.data.keys()),
                "analysis_duration": "short"  # You could add actual duration calculation
            }
        }
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

# Optional: Add endpoint for supported analysis types
@router.get("/analysis-types")
async def get_analysis_types():
    """Return list of supported analysis types"""
    return {
        "supported_types": [
            {
                "name": "general",
                "description": "Overall energy usage analysis and recommendations"
            },
            {
                "name": "savings",
                "description": "Focus on cost-saving opportunities"
            },
            {
                "name": "patterns",
                "description": "Detailed analysis of usage patterns and anomalies"
            }
        ]
    }