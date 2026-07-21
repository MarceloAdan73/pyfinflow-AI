from sqlalchemy.orm import Session

from app.repositories.base_repo import BaseRepository
from app.repositories.postgres_repo import (
    TransactionRepository as PgTransactionRepo,
    BudgetRepository as PgBudgetRepo,
    GoalRepository as PgGoalRepo,
    UserRepository as PgUserRepo,
    ChatRepository as PgChatRepo,
    AIProviderConfigRepository as PgAIConfigRepo,
)


class RepositoryFactory:
    """Factory para crear repositorios según el entorno"""

    def __init__(self, session: Session):
        self.session = session

    @property
    def transactions(self) -> PgTransactionRepo:
        return PgTransactionRepo(self.session)

    @property
    def budgets(self) -> PgBudgetRepo:
        return PgBudgetRepo(self.session)

    @property
    def goals(self) -> PgGoalRepo:
        return PgGoalRepo(self.session)

    @property
    def users(self) -> PgUserRepo:
        return PgUserRepo(self.session)

    @property
    def chats(self) -> PgChatRepo:
        return PgChatRepo(self.session)

    @property
    def ai_config(self) -> PgAIConfigRepo:
        return PgAIConfigRepo(self.session)
