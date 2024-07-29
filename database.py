from aiosqlite import connect

from typing import Literal

from dotenv import load_dotenv
from os import getenv


load_dotenv()
DB_HOST = getenv('DATABASE_PATH')


# TABLE "state" STRUCTURE:
# 0: user_id
# 1: state
# 2: other_user_id if state is "question"

# TABLE "questions" STRUCTURE:
# 0: user_id
# 1: full_name
# 2: question_id
# 3: question_text


async def get_length() -> int:
    async with connect(DB_HOST) as _DB:
        return len(await _DB.execute_fetchall('SELECT * FROM questions'))


async def dloadQuestion(
    user_id: int, full_name: str, question: str
) -> None:
    async with connect(DB_HOST) as _DB:
        qid = (await get_length()) + 1
        await _DB.execute(
            'INSERT INTO questions (user, name, question_id, question) VALUES'
            f' ({user_id}, "{full_name}", {qid}, "{question}")'
        )
        return await _DB.commit()


async def getState(user_id: int) -> int:
    async with connect(DB_HOST) as _DB:
        async with _DB.execute_fetchall(
            f'SELECT state FROM states WHERE user={user_id}'
        ) as _STAGE:
            if _STAGE[0][1] == 'question':
                return _STAGE[0][2]
            return 0


async def setState(user_id: int, state: Literal['question', 'main'], other_user: int) -> None:
    async with connect(DB_HOST) as _DB:
        async with _DB.execute_fetchall(
            f'SELECT state FROM states WHERE user={user_id}'
        ) as _STAGE:
            if not _STAGE:
                if not other_user:
                    await _DB.execute(
                        'INSERT INTO states (user, state) VALUES '
                        f'({user_id}, {state})'
                    )
                else:
                    await _DB.execute(
                        'INSERT INTO states (user, state) VALUES '
                        f'({user_id}, {state})'
                    )

            else:
                await _DB.execute(
                    f'UPDATE states SET state="{state}" WHERE user={user_id}'
                )
    return await _DB.commit()


async def getRow() -> tuple[int, str]:
    ...
