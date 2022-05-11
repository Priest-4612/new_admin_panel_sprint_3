import time
from functools import wraps
from pathlib import Path

RETRIES_EXCEPTION = (
    'Повторный запуск. Функция: {function}, ',
    'завершила рабобу с ошибкой: {exceprion}',
)
FINALLY_EXCEPTION = (
    'Превышено максимальное время ожидания выполнения функции: {function},',
    'приложение завершило работу с ошибкой {exceprion}',
)


def backoff(start_sleep_time=0.1, factor=2, border_sleep_time=10):
    """
    Функция для повторного выполнения функции через некоторое время.

    Использует наивный экспоненциальный рост времени повтора (factor)
    до граничного времени ожидания (border_sleep_time).

    Формула:
        t = start_sleep_time * 2^(n) if t < border_sleep_time
        t = border_sleep_time if t >= border_sleep_time.

    Args:
        start_sleep_time (float): начальное время повтора
        factor (int): во сколько раз нужно увеличить время ожидания
        border_sleep_time (int): граничное время ожидания

    Returns:
        func: Кезультат выполнения функции
    """

    def func_wrapper(func):
        @wraps(func)
        def inner(*args, **kwargs):
            retries = 0
            while True:
                sleep_time = start_sleep_time * factor ** retries
                try:
                    return func(*args, **kwargs)
                except Exception as exception:
                    if sleep_time > border_sleep_time:
                        error_message = FINALLY_EXCEPTION.format(
                            function=func.__name__,
                            exception=exception,
                        )
                        logging.error(error_message)
                        raise TimeoutError(error_message)
                    logging.info(RETRIES_EXCEPTION.format(
                        function=func.__name__,
                        exception=exception,
                    ))
                    time.sleep(sleep_time)
                    retries += 1
        return inner
    return func_wrapper


if __name__ == '__main__':
    import logging

    BASE_PATH = Path(__file__).resolve()
    PATH_TO_LOG = BASE_PATH.parents[3].joinpath('logs', 'backoff')

    _log_format = (
        '%(asctime)s - [%(levelname)s] -  %(name)s - ',
        '(%(filename)s).%(funcName)s(%(lineno)d) - %(message)s',
    )

    logging.basicConfig(
        level=logging.DEBUG,
        format=_log_format,
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(
                filename=PATH_TO_LOG, mode='a', encoding='utf8',
            ),
        ])