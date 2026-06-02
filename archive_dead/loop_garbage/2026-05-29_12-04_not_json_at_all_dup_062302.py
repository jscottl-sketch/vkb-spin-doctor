# Old JSON‑based endpoint
@app.route('/v1/machine:input', methods=['POST'])
def input_json():
    payload = request.get_json()
    # …process JSON…

# New URL‑encoded endpoint
@app.route('/v1/machine:input', methods=['POST'])
def input_form():
    # Retrieve form fields
    key = request.form.get('key')
    action = request.form.get('action')
    axis = request.form.get('axis')
    value = request.form.get('value')
    button = request.form.get('button')
    # Dispatch to the appropriate handler
    if key and action:
        handle_key(int(key), action)
    elif axis and value:
        handle_axis(int(axis), float(value))
    elif button and action:
        handle_button(int(button), action)
    else:
        return 'Invalid parameters', 400
    return 'OK', 200
