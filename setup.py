from aiosqlite import connect
from dotenv import load_dotenv
from functools import lru_cache
from logger import Logger, LoggingLevel
from os import getenv
from asyncio import run as _runner


load_dotenv()
DB_HOST = getenv('DATABASE_PATH')
logger = Logger()


@lru_cache()
async def setup() -> None:
    await logger.asyncLogger(
        'The initial setup is being performed...',
        module='WAWILON-ANONQUESTIONS',
        log_level=LoggingLevel.INFO
    )

    async with connect(DB_HOST) as _DB:
        try:
            await _DB.execute(
                'CREATE TABLE IF NOT EXISTS questions ('
                'user INTEGER NOT NULL, '
                'full_name TEXT, '
                'question_id INTEGER NOT NULL, '
                'question TEXT,'
                'other_user INTEGER NOT NULL'
                ')'
            )
            await logger.asyncLogger(
                'Created table "questions"',
                module='WAWILON-ANONQUESTIONS',
                log_level=LoggingLevel.INFO
            )

            await _DB.execute(
                'CREATE TABLE IF NOT EXISTS states ('
                'user INTEGER NOT NULL, '
                'state TEXT NOT NULL, '
                'other_user INTEGER'
                ')'
            )
            await logger.asyncLogger(
                'Created table "states"',
                module='WAWILON-ANONQUESTIONS',
                log_level=LoggingLevel.INFO
            )

            await _DB.commit()
            return await logger.asyncLogger(
                'Bot setup passed without errors.',
                module='WAWILON-ANONQUESTIONS',
                log_level=LoggingLevel.INFO
            )
        except BaseException as errorText:
            return await logger.asyncLogger(
                f'Error: {errorText}',
                module='WAWILON-ANONQUESTIONS'
            )

_runner(setup())
