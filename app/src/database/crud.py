from typing import List, Type, Any, Optional
from sqlmodel import SQLModel
from sqlalchemy import select,distinct,delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, SQLModel

async def update_field(
    session: AsyncSession,
    model: SQLModel,
    column_name_to_update: str,
    where_column: str,
    where_value,
    new_value
):
    """
    Asynchronously updates a specific field of a record in a SQLModel-based model based on a condition.

    Parameters:
    ----------
    session : AsyncSession
        The active asynchronous database session used to execute the transaction.
    
    model : SQLModel
        The SQLModel representing the table where the update will be performed.
    
    column_name_to_update : str
        The name of the column to be updated.
    
    where_column : str
        The name of the column used as a condition (WHERE clause) to find the record.
    
    where_value : Any
        The value to match in the `where_column` to locate the target record.
    
    new_value : Any
        The new value to assign to the `column_name_to_update`.

    Raises:
    ----------
    ValueError:
        If no record matching the condition is found.

    Returns:
    ----------
    SQLModel:
        The updated instance of the model with the new value applied.


    """
    statement = select(model).where(getattr(model, where_column) == where_value)
    result = await session.execute(statement)
    instance = result.scalars().one_or_none()

    if instance is None:
        raise ValueError(f"No {model.__name__} found with {where_column} = {where_value}")

    # Update the specified column with the new value
    setattr(instance, column_name_to_update, new_value)
    session.add(instance)
    return instance

async def exists_in(
    model: Type[SQLModel],
    items: List[str],
    column_name: str,
    session: AsyncSession
) -> List[str]:
    """
    Check if items exist in the given model's table based on the specified column.

    Args:
        model (Type[SQLModel]): The SQLModel class representing the database table.
        items (List[str]): A list of items to check for existence.
        column_name (str): The name of the column to check against.
        session (AsyncSession): The SQLAlchemy AsyncSession instance.

    Returns:
        List[str]: A list of items that exist in the table.
    """
    column = getattr(model, column_name)
    query = select(distinct(column)).where(column.in_(items))
    result = await session.execute(query)
    existing_items = result.scalars().all()
    return existing_items

async def search_value(
    model: Type[SQLModel],
    value: Any,
    column_name: str,
    session: AsyncSession,
    distinct_results: bool = False,
    select_values: Optional[List[Any]] = None
) -> List[Any]:
    """
    Search for values in a specific column of a SQLModel table, 
    with optional flags to return distinct results or select specific columns.

    Args:
        model (Type[SQLModel]): The SQLModel class representing the database table.
        value (Any): The value to search for in the specified column.
        column_name (str): The name of the column to perform the search on.
        session (AsyncSession): An active SQLAlchemy AsyncSession instance.
        distinct_results (bool, optional): If True, only distinct results will be returned. Defaults to False.
        select_values (Optional[List[Any]], optional): Specific columns to select. If None, the entire model is selected.

    Returns:
        List[Any]: A list of values matching the search criteria.
    """
    try:
        column = getattr(model, column_name)
        query_select = select(*select_values) if select_values else select(model)
        query = query_select.where(column == value)

        if distinct_results:
            query = query.distinct()

        result = await session.execute(query)
        response = result.scalars().all()
        return response
    except Exception as e:
        print(f"Error during query execution: {e}")
        return []
    
    
async def delete_in(
    model: Type[SQLModel],
    items: List[str],
    column_name: str,
    session: AsyncSession
) -> int:
    """
    Delete items from the given model's table based on the specified column.

    Args:
        model (Type[SQLModel]): The SQLModel class representing the database table.
        items (List[str]): A list of items to delete.
        column_name (str): The name of the column to check against.
        session (AsyncSession): The SQLAlchemy AsyncSession instance.

    Returns:
        int: The number of rows deleted.
    """
    column = getattr(model, column_name)
    query = delete(model).where(column.in_(items))
    result = await session.execute(query)
    await session.commit()
    return result.rowcount
