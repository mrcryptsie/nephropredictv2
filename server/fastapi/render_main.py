from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Dict, Any, Optional
import uvicorn
import numpy as np
from lazy_model import LazyIRCModel

# Initialize the FastAPI app
app = FastAPI(
    title="NéphroPredict API",
    description="API for predicting the stage of IRC (Insuffisance Rénale Chronique)",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load the model on startup (in background)
model = LazyIRCModel()

# Input data model
class PredictionInput(BaseModel):
    """Input data for IRC stage prediction"""
    créatinine_mg_L: float = Field(alias="Créatinine (mg/L)", description="Blood creatinine level in mg/L")
    urée_g_L: float = Field(alias="Urée (g/L)", description="Blood urea level in g/L")
    age: int = Field(alias="Age", description="Patient's age in years")
    sodium_meq_L: float = Field(alias="Na^+ (meq/L)", description="Blood sodium level in meq/L")
    ta_systole: float = Field(alias="TA (mmHg)/Systole", description="Systolic blood pressure in mmHg")
    choc_de_pointe: int = Field(alias="Choc de Pointe/Perçu", description="Presence of shock, 0 or 1")
    sexe_M: int = Field(alias="Sexe_M", description="Gender: 1 for male, 0 for female")
    anémie_true: int = Field(alias="Anémie_True", description="Presence of anemia: 1 if present, 0 otherwise")
    glasgow: float = Field(alias="Score de Glasgow (/15)", description="Glasgow score on a scale of 3 to 15")
    tabac_true: int = Field(alias="Enquête Sociale/Tabac_True", description="Tobacco use: 1 if yes, 0 if no")
    alcool_true: int = Field(alias="Enquête Sociale/Alcool_True", description="Alcohol consumption: 1 if yes, 0 if no")

    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "Créatinine (mg/L)": 42.0,
                "Urée (g/L)": 1.14,
                "Age": 68,
                "Na^+ (meq/L)": 142.0,
                "TA (mmHg)/Systole": 130.0,
                "Choc de Pointe/Perçu": 0,
                "Sexe_M": 1,
                "Anémie_True": 1,
                "Score de Glasgow (/15)": 15.0,
                "Enquête Sociale/Tabac_True": 0,
                "Enquête Sociale/Alcool_True": 1
            }
        }
    )

# Stage probability model
class StageProbability(BaseModel):
    stage: int
    probability: float

# Feature importance model
class FeatureImportance(BaseModel):
    feature: str
    importance: float

# Prediction output model
class PredictionOutput(BaseModel):
    predicted_stage: int
    confidence: float
    stage_probabilities: List[StageProbability]
    feature_importance: List[FeatureImportance]

# Model status model
class ModelStatus(BaseModel):
    status: str
    model_loaded: bool
    model_loading: bool
    model_type: Optional[str] = None
    
    model_config = ConfigDict(
        protected_namespaces=()
    )

@app.get("/")
async def root():
    return {"message": "Welcome to the NéphroPredict API. Use /predict endpoint to make IRC stage predictions."}

@app.get("/health")
async def health_check():
    """Endpoint for health checks"""
    status = model.get_status()
    return {"status": "ok", "model_status": status}

@app.get("/model/status", response_model=ModelStatus)
async def model_status():
    """Get the current status of the model"""
    status = model.get_status()
    return ModelStatus(
        status="ok" if status["model_loaded"] else "loading",
        model_loaded=status["model_loaded"],
        model_loading=status["model_loading"],
        model_type=status["model_type"]
    )

@app.post("/predict", response_model=PredictionOutput)
async def predict(input_data: PredictionInput):
    try:
        # Convert input to the format expected by the model
        input_dict = {
            'Créatinine (mg/L)': input_data.créatinine_mg_L,
            'Urée (g/L)': input_data.urée_g_L,
            'Age': input_data.age,
            'Na^+ (meq/L)': input_data.sodium_meq_L,
            'TA (mmHg)/Systole': input_data.ta_systole,
            'Choc de Pointe/Perçu': input_data.choc_de_pointe,
            'Score de Glasgow (/15)': input_data.glasgow,
            'Sexe_M': input_data.sexe_M,
            'Anémie_True': input_data.anémie_true,
            'Enquête Sociale/Tabac_True': input_data.tabac_true,
            'Enquête Sociale/Alcool_True': input_data.alcool_true
        }
        
        # Make prediction
        prediction_result = model.predict(input_dict)
        
        # Get stage probabilities
        probabilities = model.get_stage_probabilities()
        stage_probs = [
            StageProbability(stage=stage, probability=prob)
            for stage, prob in probabilities.items()
        ]
        
        # Get feature importance
        feature_imp = model.get_feature_importance()
        feature_importance = [
            FeatureImportance(feature=feat, importance=imp)
            for feat, imp in feature_imp.items()
        ]
        
        # Return prediction results
        return PredictionOutput(
            predicted_stage=prediction_result,
            confidence=probabilities[prediction_result],
            stage_probabilities=stage_probs,
            feature_importance=feature_importance
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

if __name__ == "__main__":
    uvicorn.run("render_main:app", host="0.0.0.0", port=8000, reload=False)