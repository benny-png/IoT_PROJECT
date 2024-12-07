# app/energy_analyzer.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
from openai import OpenAI
import json
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

router = APIRouter()

# Get API key with error handling
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
if not OPENAI_API_KEY:
    print("Warning: OPENAI_API_KEY not found in environment variables")
    MOCK_MODE = True
else:
    MOCK_MODE = False
    client = OpenAI(api_key=OPENAI_API_KEY)

class EnergyData(BaseModel):
    data: Dict[str, Any]
    analysis_type: Optional[str] = "general"

def get_mock_response(data: Dict, analysis_type: str) -> Dict:
    """Return mock response for testing without API key"""
    mock_recommendations = {
        "general": """
            Mock General Recommendations:
            1. Your daily energy usage appears to be highest during 2-4 PM
            2. HVAC system accounts for 40% of your consumption
            3. Recommended Actions:
               - Adjust thermostat settings
               - Install LED lighting
               - Schedule equipment maintenance
            4. Estimated savings potential: 15-20%
        """,
        "savings": """
            Mock Savings Analysis:
            1. Peak Usage: 2-4 PM daily
            2. Potential Savings: $200-300 monthly
            3. Priority Actions:
               - Optimize HVAC scheduling
               - Update lighting systems
               - Install smart controls
            4. ROI Timeline: 6-8 months
        """,
        "patterns": """
            Mock Pattern Analysis:
            1. Usage Trends:
               - Weekday peaks: Morning and Evening
               - Weekend: More consistent usage
            2. Anomalies: Unusual spike every Friday
            3. Industry Comparison: 20% above average
            4. Optimization Opportunities Identified
        """
    }
    
    return {
        "timestamp": datetime.now().isoformat(),
        "analysis_type": analysis_type,
        "recommendations": mock_recommendations.get(analysis_type, mock_recommendations["general"]),
        "data_summary": {
            "fields_analyzed": list(data.keys()),
            "analysis_duration": "short",
            "mode": "MOCK - No OpenAI API Key"
        }
    }

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
        if MOCK_MODE:
            return get_mock_response(request.data, request.analysis_type)

        if not request.data:
            raise HTTPException(status_code=400, detail="No data provided for analysis")

        prompt = generate_prompt(request.data, request.analysis_type)
        
        try:
            completion = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an energy efficiency expert specializing in data analysis and providing actionable recommendations."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            recommendations = completion.choices[0].message.content
            
        except Exception as api_error:
            print(f"OpenAI API Error: {str(api_error)}")
            return get_mock_response(request.data, request.analysis_type)

        response = {
            "timestamp": datetime.now().isoformat(),
            "analysis_type": request.analysis_type,
            "recommendations": recommendations,
            "data_summary": {
                "fields_analyzed": list(request.data.keys()),
                "analysis_duration": "short"
            }
        }
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

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

@router.get("/status")
async def get_api_status():
    """Check API status and mode"""
    return {
        "status": "operational",
        "mode": "mock" if MOCK_MODE else "live",
        "timestamp": datetime.now().isoformat()
    }