from __future__ import annotations

import json
from sqlalchemy.orm import Session

from app.errors import ConcurrencyConflictError
from app.models.user_preference import UserPreference
from app.schemas.preferences import UserPreferenceRead, UserPreferenceUpdate
from app.services.persistence import commit_changes


def get_or_create_user_preferences(session: Session, user_id: str) -> UserPreference:
    """Recupera ou cria as preferências padrão de leitura do usuário."""
    pref = session.get(UserPreference, user_id)
    if pref is None:
        pref = UserPreference(
            user_id=user_id,
            active_superclass="mecanica",
            superclass_intensity=1.0,
            preferred_view_mode="grid",
            tree_collapsed_state="[]",
            font_family="garamond",
            font_scale=1.0,
            theme_mode="dark",
            version=1,
        )
        session.add(pref)
        commit_changes(session)
        session.refresh(pref)
    return pref


def update_user_preferences(
    session: Session,
    user_id: str,
    payload: UserPreferenceUpdate,
) -> UserPreference:
    """Atualiza preferências de leitura com controle otimista de concorrência."""
    pref = get_or_create_user_preferences(session, user_id)

    # Validação OCC
    if payload.expected_version is not None and payload.expected_version != pref.version:
        server_data = UserPreferenceRead.model_validate(pref).model_dump(mode="json")
        raise ConcurrencyConflictError(
            entity_id=0,
            entity_type="preference",
            server_version=pref.version,
            server_updated_at=pref.updated_at,
            server_data=server_data,
            detail="Conflito de concorrência: suas preferências foram atualizadas em outro dispositivo.",
        )

    fields_to_update = payload.model_fields_set - {"expected_version"}

    for field_name in fields_to_update:
        val = getattr(payload, field_name)
        if field_name == "tree_collapsed_state":
            if val is not None:
                pref.tree_collapsed_state = json.dumps(val)
        else:
            if val is not None:
                setattr(pref, field_name, val)

    pref.version += 1
    commit_changes(session)
    session.refresh(pref)
    return pref
