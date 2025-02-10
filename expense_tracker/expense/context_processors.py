# myapp/context_processors.py

def base_template(request):
    """
    Determines the base template based on the user's type.
    """
    # Set a default value; adjust as needed
    template = 'base.html'
    
    if request.user.is_authenticated:
        if request.user.user_type == 'admin':
            template = 'base.html'
        elif request.user.user_type in ['ted', 's2l']:
            template = 'department_base.html'
        # Add more conditions if necessary

    return {'base_template': template}
