# utils.py
def format_response(status, return_data=None, error_code=None, error_descr=None):
    if status:
        return {
            "status": True,
            "returnData": return_data
        }
    else:
        return {
            "status": False,
            "errorCode": error_code,
            "errorDescr": error_descr
        }
