import inspect

from loguru import logger



def log_error_with_method_info(exception: Exception):
    frame_info = inspect.stack()[2]
    caller_frame = frame_info.frame
    caller_globals = caller_frame.f_globals

    class_name = None
    for _, value in caller_globals.items():
        if inspect.isclass(value) and issubclass(value, object):
            if value.__dict__.get(frame_info.function, None) is not None:
                class_name = value.__name__
                break

    method_name = frame_info.function
    module_name = caller_globals.get('__name__', None)
    line_number = frame_info.lineno

    logger.opt(exception=exception).critical(
        f"Unexpected error in method {class_name}.{method_name} "
        f"of module {module_name}, line {line_number}: {exception}"
    )

    raise exception