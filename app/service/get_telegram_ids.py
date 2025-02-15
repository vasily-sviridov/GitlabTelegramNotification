from app.models.webhook import Webhook
import os
from dotenv import load_dotenv
from psycopg2 import OperationalError, connect
from app.models.object_infos import ObjectType
OBJECT_INFOS = ObjectType


async def _get_assignee_ids(webhook: Webhook):
    object_kind = webhook.object_kind
    if object_kind == OBJECT_INFOS.NOTE.value:
        note_type = webhook.object_attributes.noteable_type
        if note_type == OBJECT_INFOS.ISSUE_NOTEABLE_TYPE.value:
            return webhook.issue.assignee_ids
        elif note_type == OBJECT_INFOS.MERGE_REQUEST_NOTEABLE_TYPE.value:
            return webhook.merge_request.assignee_ids.extend(webhook.merge_request.reviewer_ids)
    elif object_kind == OBJECT_INFOS.ISSUE.value:
        return webhook_info.assignee_ids
    elif object_kind == OBJECT_INFOS.MERGE_REQUEST.value:
        return webhook_info.assignee_ids.extend(webhook_info.reviewer_ids)
    elif object_kind == OBJECT_INFOS.PIPELINE.value:
        return webhook_info.user.id


async def get_telegram_ids(webhook: Webhook):
    target_telegram_ids = []
    load_dotenv(".env")
    connection = connect(os.environ.get("DSN"))
    cursor = connection.cursor()
    cursor.execute("""
    select telegram_id, gitlab_id from tg_gitlab.telegram_gitlab order by gitlab_id""")
    result = cursor.fetchall()
    for assingee_id in await _get_assignee_ids(webhook):
        for row in result:
            telegram_id = row[0]
            gitlab_id = row[1]
            if assingee_id == gitlab_id:
                target_telegram_ids.append(telegram_id)

    if len(target_telegram_ids) > 0:
        return target_telegram_ids

    return [row[0] for row in result]
