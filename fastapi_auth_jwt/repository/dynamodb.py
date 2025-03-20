from typing import Any, Optional
import os

from pynamodb.models import Model
from pynamodb.attributes import UnicodeAttribute
from pynamodb.exceptions import DoesNotExist

from ..config.storage import DynamoDBConfig
from .base import BaseRepository


class SessionModel(Model):
    """
    PynamoDB model for storing session data in DynamoDB.

    Attributes:
        key (str): The session key (partition key).
        value (str): The session value.
    """

    class Meta:
        table_name = os.environ.get("DynamoDBSessionTableName", "session_store")
        region = "us-east-1"
        host = None  # Set dynamically from config

    key = UnicodeAttribute(hash_key=True)
    value = UnicodeAttribute()

    @classmethod
    def setup(cls, config: DynamoDBConfig):
        """
        Initialize the table based on the provided config.

        Args:
            config (DynamoDBConfig): The configuration object containing DynamoDB settings.
        """
        cls.Meta.table_name = config.table_name
        cls.Meta.region = config.region
        cls.Meta.host = config.endpoint_url

        if not cls.exists():
            cls.create_table(wait=True)


class DynamoDBRepository(BaseRepository):
    """
    Repository implementation using DynamoDB with PynamoDB.

    This class provides an interface to interact with DynamoDB as a key-value store.
    """

    def __init__(self, config: DynamoDBConfig):
        """
        Initialize the repository with a given configuration.

        Args:
            config (DynamoDBConfig): The configuration object containing DynamoDB connection details.
        """
        self._config = config
        SessionModel.setup(config)

    async def get(self, key: str) -> Optional[Any]:
        """
        Retrieve a value from the DynamoDB store by its key.

        Args:
            key (str): The key for the value to retrieve.

        Returns:
            Optional[Any]: The value associated with the key, or None if the key is not found.
        """
        try:
            session = SessionModel.get(key)
            return session.value
        except DoesNotExist:
            return None

    async def set(self, key: str, value: str) -> None:
        """
        Store a value in the DynamoDB store.

        Args:
            key (str): The key to associate with the value.
            value (str): The value to store.

        Returns:
            None
        """
        session = SessionModel(key=key, value=value)
        session.save()

    async def delete(self, key: str) -> None:
        """
        Delete a value from the DynamoDB store by its key.

        Args:
            key (str): The key for the value to delete.

        Returns:
            None
        """
        try:
            session = SessionModel.get(key)
            session.delete()
        except DoesNotExist:
            pass


__all__ = ["DynamoDBRepository"]
