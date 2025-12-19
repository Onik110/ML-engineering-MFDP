from sqlmodel import Session, select
from models.prediction import MLPrediction

class PredictionService:
    def __init__(self, session: Session):
        self.session = session

    def add_prediction(self, prediction: MLPrediction) -> MLPrediction:
        self.session.add(prediction)
        self.session.commit()
        self.session.refresh(prediction)
        return prediction

    def get_history(self, user_id: int) -> list[MLPrediction]:
        return self.session.exec(
            select(MLPrediction)
            .where(MLPrediction.user_id == user_id)
            .order_by(MLPrediction.timestamp.desc())
        ).all()

