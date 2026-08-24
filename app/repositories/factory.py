from sqlalchemy.orm import Session

from app.repositories.postgres_repo import (
    AIProviderConfigRepository as PgAIConfigRepo,
)
from app.repositories.postgres_repo import (
    BudgetRepository as PgBudgetRepo,
)
from app.repositories.postgres_repo import (
    ChatRepository as PgChatRepo,
)
from app.repositories.postgres_repo import (
    GoalRepository as PgGoalRepo,
)
from app.repositories.postgres_repo import (
    TransactionRepository as PgTransactionRepo,
)
from app.repositories.postgres_repo import (
    UserRepository as PgUserRepo,
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
