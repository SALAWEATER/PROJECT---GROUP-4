from sqlalchemy.orm import Session
from ..business.models import UserICDLink

class ICDRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_link(self, user_id: int, entity_id: str, entity_title: str, notes: str = None):
        link = UserICDLink(
            user_id=user_id,
            entity_id=entity_id,
            entity_title=entity_title,
            notes=notes
        )
        self.db.add(link)
        self.db.commit()
        return link

    def get_user_links(self, user_id: int):
        return self.db.query(UserICDLink)\
            .filter(UserICDLink.user_id == user_id)\
            .order_by(UserICDLink.created_at.desc())\
            .all()