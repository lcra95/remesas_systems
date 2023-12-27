import sys
from helpers.response_handler import handle_api_response


def handle_exception(error):
    exc_type, _, exc_tb = sys.exc_info()
    exc_name = exc_type.__name__
    fname = exc_tb.tb_frame.f_code.co_filename
    line_no = exc_tb.tb_lineno
    error_message = f'Error: {error} ({exc_name}) - File: {fname}, Line: {line_no}'
    return handle_api_response(success=False, sys_error=error_message, status_code=500, error_message=str(error))