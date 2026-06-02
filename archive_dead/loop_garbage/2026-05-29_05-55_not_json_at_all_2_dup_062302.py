
*`IInputManager`* is the existing abstraction that already handles native keyboard/joystick events.  
Add an extension method `Inject(InputEvent ev)` if one does not already exist.

### D. Injection logic

Add a helper class `InputInjectionDto` to convert the JSON payload into the internal event model:

