
*Notes*  
* `type` is a case‑insensitive string.  
* For *keyboard* events, `code` is the hardware scan‑code and `value` must be `pressed` or `released`.  
* For *joystick* events, `code` may be either `x`, `y`, or a button identifier (`b0`‑`b7`).  `value` is an integer in the range –127 … 127 for axes and either `pressed`/`released` for buttons.  

### 1.4. Implementation  

#### 1.4.1. Create the controller

File: `src/Server/Controllers/InputController.cs`

