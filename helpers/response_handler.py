def handle_api_response(success=True, data_name='data', data=None, error_message=None, status_code=200, sys_error=None):
    if success:
        response = {
            'status_code': status_code,
            'status': 'success',
            'msj': 'OK',
            data_name: data

        }
    else:
        response = {
            'status_code': status_code,
            'status': 'fail',
            'msj': error_message,
            'sys_error': sys_error
        }
    return response