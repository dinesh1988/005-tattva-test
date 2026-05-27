"""
Database Module for VedAstroPy API
===================================
Azure Table Storage integration for storing Psychic Profiles and Daily Predictions.

Supports:
1. Azure Table Storage (Production) — set USE_AZURE_TABLES=true + AZURE_STORAGE_CONNECTION_STRING
2. In-memory storage (Development/Testing) — default (no env vars needed)
"""

import os
import uuid
import json
from datetime import datetime
from typing import Optional, List, Dict, Any

# =============================================================================
# Configuration
# =============================================================================

USE_AZURE_TABLES = os.getenv("USE_AZURE_TABLES", "false").lower() == "true"

AZURE_STORAGE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING", "")
AZURE_TABLE_PROFILES = os.getenv("AZURE_TABLE_PROFILES", "TattvaProfiles")
AZURE_TABLE_DAILY    = os.getenv("AZURE_TABLE_DAILY",    "TattvaDaily")
AZURE_TABLE_USERS    = os.getenv("AZURE_TABLE_USERS",    "TattvaUsers")


# =============================================================================
# In-Memory Storage (Development)
# =============================================================================

_memory_store: Dict[str, Dict[str, Any]] = {}


async def _save_to_memory(profile: dict, user_id: str) -> str:
    """Save profile to in-memory storage."""
    profile_id = str(uuid.uuid4())
    profile['id'] = profile_id
    profile['user_id'] = user_id
    profile['created_at'] = datetime.utcnow().isoformat()
    profile['_partition_key'] = user_id
    _memory_store[profile_id] = profile
    return profile_id


async def _get_from_memory(profile_id: str) -> Optional[dict]:
    """Get profile from in-memory storage."""
    return _memory_store.get(profile_id)


async def _get_user_profiles_memory(user_id: str, limit: int = 10) -> List[dict]:
    """Get all profiles for a user from in-memory storage."""
    profiles = [p for p in _memory_store.values()
                if p.get('user_id') == user_id and p.get('type') != 'daily_prediction']
    return sorted(profiles, key=lambda x: x.get('created_at', ''), reverse=True)[:limit]


# =============================================================================
# Azure Table Storage (Production)
# =============================================================================

_profiles_table = None
_daily_table     = None
_users_table     = None


def _init_azure():
    """Lazy-init Azure Table Storage sync clients and create tables if needed."""
    global _profiles_table, _daily_table, _users_table

    if _profiles_table is not None:
        return

    try:
        from azure.data.tables import TableServiceClient
    except ImportError:
        raise RuntimeError(
            "azure-data-tables not installed. Run: pip install azure-data-tables"
        )

    if not AZURE_STORAGE_CONNECTION_STRING:
        raise RuntimeError(
            "AZURE_STORAGE_CONNECTION_STRING env var is not set. "
            "Set USE_AZURE_TABLES=false to use in-memory storage instead."
        )

    service = TableServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)

    for table_name in [AZURE_TABLE_PROFILES, AZURE_TABLE_DAILY, AZURE_TABLE_USERS]:
        try:
            service.create_table_if_not_exists(table_name)
        except Exception:
            pass  # Already exists

    _profiles_table = service.get_table_client(AZURE_TABLE_PROFILES)
    _daily_table    = service.get_table_client(AZURE_TABLE_DAILY)
    _users_table    = service.get_table_client(AZURE_TABLE_USERS)
    print(f"Connected to Azure Table Storage: {AZURE_TABLE_PROFILES}, {AZURE_TABLE_DAILY}, {AZURE_TABLE_USERS}")


# --- Profiles (async wrappers around sync Azure client) ----------------------

import asyncio


async def _save_to_azure(profile: dict, user_id: str) -> str:
    _init_azure()
    profile_id = str(uuid.uuid4())
    document = {**profile, "id": profile_id, "user_id": user_id,
                "created_at": datetime.utcnow().isoformat()}
    entity = {
        "PartitionKey": user_id,
        "RowKey":       profile_id,
        "ProfileJson":  json.dumps(document),
    }
    await asyncio.to_thread(_profiles_table.upsert_entity, entity)
    return profile_id


async def _get_from_azure(profile_id: str) -> Optional[dict]:
    _init_azure()

    def _query():
        for entity in _profiles_table.query_entities(f"RowKey eq '{profile_id}'"):
            return json.loads(entity["ProfileJson"])
        return None

    return await asyncio.to_thread(_query)


async def _get_user_profiles_azure(user_id: str, limit: int = 10) -> List[dict]:
    _init_azure()

    def _query():
        results = []
        for entity in _profiles_table.query_entities(f"PartitionKey eq '{user_id}'"):
            try:
                results.append(json.loads(entity["ProfileJson"]))
            except Exception:
                pass
            if len(results) >= limit:
                break
        return sorted(results, key=lambda x: x.get('created_at', ''), reverse=True)

    return await asyncio.to_thread(_query)


# =============================================================================
# Public Interface (Auto-selects storage backend)
# =============================================================================

async def get_db():
    """Dependency for database access."""
    return {"backend": "azure_tables" if USE_AZURE_TABLES else "memory"}


async def save_profile(profile: dict, user_id: str) -> str:
    """Save a psychic profile. Returns generated profile ID."""
    if USE_AZURE_TABLES:
        return await _save_to_azure(profile, user_id)
    return await _save_to_memory(profile, user_id)


async def get_profile_by_id(profile_id: str) -> Optional[dict]:
    """Retrieve a profile by its ID."""
    if USE_AZURE_TABLES:
        return await _get_from_azure(profile_id)
    return await _get_from_memory(profile_id)


async def get_profiles_by_user(user_id: str, limit: int = 10) -> List[dict]:
    """Get all profiles for a specific user."""
    if USE_AZURE_TABLES:
        return await _get_user_profiles_azure(user_id, limit)
    return await _get_user_profiles_memory(user_id, limit)


async def delete_profile(profile_id: str, user_id: str = None) -> bool:
    """Delete a profile. Returns True if deleted, False if not found."""
    if USE_AZURE_TABLES:
        _init_azure()
        try:
            pk = user_id
            if not pk:
                profile = await _get_from_azure(profile_id)
                if not profile:
                    return False
                pk = profile.get('user_id')
            await asyncio.to_thread(_profiles_table.delete_entity,
                                    partition_key=pk, row_key=profile_id)
            return True
        except Exception:
            return False
    else:
        if profile_id in _memory_store:
            del _memory_store[profile_id]
            return True
        return False


# =============================================================================
# Daily Prediction Storage (Cache Layer)
# =============================================================================

def save_daily_prediction(prediction: dict, user_id: str, date: str) -> str:
    """
    Save a daily prediction with date-based cache key (user_id + date).
    Sync function — safe to call from non-async contexts.
    """
    doc_id = f"{user_id}_{date}"

    if USE_AZURE_TABLES:
        _init_azure()
        try:
            entity = {
                "PartitionKey":    user_id,
                "RowKey":          date,
                "PredictionJson":  json.dumps({
                    'id': doc_id, 'user_id': user_id, 'date': date,
                    'created_at': datetime.utcnow().isoformat(),
                    **prediction
                }),
            }
            _daily_table.upsert_entity(entity)
        except Exception as e:
            print(f"Warning: Could not save daily prediction to Azure Tables: {e}")
    else:
        _memory_store[doc_id] = {
            'id': doc_id, 'user_id': user_id, 'date': date,
            'created_at': datetime.utcnow().isoformat(),
            'type': 'daily_prediction',
            **prediction
        }

    return doc_id


def get_daily_prediction(user_id: str, date: str) -> Optional[dict]:
    """
    Retrieve a cached daily prediction by user + date.
    Sync function — safe to call from non-async contexts.
    """
    if USE_AZURE_TABLES:
        _init_azure()
        try:
            entity = _daily_table.get_entity(partition_key=user_id, row_key=date)
            return json.loads(entity["PredictionJson"])
        except Exception:
            return None
    else:
        doc_id = f"{user_id}_{date}"
        return _memory_store.get(doc_id)


# =============================================================================
# User Natal Profile Storage (one record per user)
# =============================================================================

async def save_user_record(user_id: str, data: dict) -> None:
    """
    Upsert the natal/phase profile record for a user.
    Keyed by user_id — overwrites any previous record for that user.
    """
    data = {**data, "user_id": user_id, "updated_at": datetime.utcnow().isoformat()}

    if USE_AZURE_TABLES:
        _init_azure()
        entity = {
            "PartitionKey": "users",
            "RowKey":       user_id,
            "RecordJson":   json.dumps(data),
        }
        await asyncio.to_thread(_users_table.upsert_entity, entity)
    else:
        _memory_store[f"_user_record_{user_id}"] = data


async def get_user_record(user_id: str) -> Optional[dict]:
    """Retrieve the stored natal/phase profile for a user, or None if not found."""
    if USE_AZURE_TABLES:
        _init_azure()

        def _query():
            try:
                entity = _users_table.get_entity(partition_key="users", row_key=user_id)
                return json.loads(entity["RecordJson"])
            except Exception:
                return None

        return await asyncio.to_thread(_query)
    else:
        return _memory_store.get(f"_user_record_{user_id}")


async def invalidate_user_daily_cache(user_id: str) -> int:
    """
    Delete all cached daily predictions for a user.
    Returns the number of entries removed.
    """
    if USE_AZURE_TABLES:
        _init_azure()

        def _delete_all():
            count = 0
            try:
                entities = list(_daily_table.query_entities(f"PartitionKey eq '{user_id}'"))
                for entity in entities:
                    try:
                        _daily_table.delete_entity(
                            partition_key=entity["PartitionKey"],
                            row_key=entity["RowKey"],
                        )
                        count += 1
                    except Exception:
                        pass
            except Exception:
                pass
            return count

        return await asyncio.to_thread(_delete_all)
    else:
        keys_to_delete = [
            k for k in list(_memory_store.keys())
            if k.startswith(f"{user_id}_") and _memory_store[k].get("type") == "daily_prediction"
        ]
        for k in keys_to_delete:
            del _memory_store[k]
        return len(keys_to_delete)

