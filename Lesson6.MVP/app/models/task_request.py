from pydantic import BaseModel, Field

class TaskRequest(BaseModel):
    input_data: str = Field(
        ..., 
        min_length=1, 
        max_length=1000,
        description="Ваши интересы (например: 'люблю LLM и архитектуру')"
    )
    model_name: str = "jug_recommender"  
