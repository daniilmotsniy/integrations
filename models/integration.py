from pylon.core.tools import log
from sqlalchemy import Integer, Column, String, Boolean, UniqueConstraint, Index
from sqlalchemy.dialects.postgresql import JSON

from tools import db_tools, db, rpc_tools


class Integration(db_tools.AbstractBaseMixin, db.Base, rpc_tools.RpcMixin):
    __tablename__ = "integration"
    __table_args__ = (
        Index(
            'ix_project_default_uc',  # Index name
            'project_id', 'name',  # Columns which are part of the index
            unique=True,
            postgresql_where=Column('is_default')  # The condition
        ),
    )

    id = Column(Integer, primary_key=True)
    name = Column(String(64), unique=False)
    project_id = Column(Integer, unique=False)
    settings = Column(JSON, unique=False, default={})
    is_default = Column(Boolean, default=False, nullable=False)
    section = Column(String(64), unique=False, nullable=False)
    description = Column(String(256), unique=False, nullable=True, default='Default integration')
    task_id = Column(String(256), unique=False, nullable=True)

    def make_default(self):
        Integration.query.filter(
            Integration.project_id == self.project_id,
            Integration.name == self.name,
            Integration.is_default == True,
            Integration.id != self.id
        ).update({Integration.is_default: False})
        self.is_default = True
        self.insert()

    def set_task_id(self, task_id: str):
        Integration.query.filter(
            Integration.id == self.id
        ).update({Integration.task_id: task_id})
        self.insert()

    def insert(self):
        if not Integration.query.filter(
            Integration.project_id == self.project_id,
            Integration.name == self.name,
            Integration.is_default == True,
        ).one_or_none():
            self.is_default = True

        super().insert()

        # self.event_manager.fire
        task_id = self.rpc.call_function_with_timeout(
            func=f'{self.name}_created_or_updated',
            timeout=30,
            integration_data=self.to_json()
        )
        if task_id:
            log.info('Got Task_ID: %s', task_id)
            # self.task_id = task_id
            # self.commit()
            self.set_task_id(task_id)





