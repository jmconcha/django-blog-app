def check_is_empty(fields):
    errors = {}
    
    for key, value in fields.items():
        if value == '':
            field_name = ' '.join(key.split('_'))
            errors[key] = f'{field_name} is required'.capitalize()
            
    return errors