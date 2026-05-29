# Morning Report — 2026-05-18 10:47

**Goal:** Explain how HidHide can be used to prevent double-input from a PS5 controller in Star Citizen
**Stop reason:** goal_met
**Iterations completed:** 1
**Total cost:** £0.003711

## Best Attempt

**ID:** 2d3e366e-e5ad-49ff-a55a-fc0759d83ffa
**Score:** 8.07

### Plan

The core problem of double-input with a PS5 controller in Star Citizen arises because Star Citizen often detects

### Work

### **How to Use HidHide to Prevent Double-Input from a PS5 Controller in Star Citizen**

#### **Problem Explanation**
The core issue of **double-input** (where inputs are registered twice) with a PS5 controller in *Star Citizen* occurs because:
- Star Citizen may detect the controller as **two separate devices** (e.g., one for the main controller and another for the touchpad).
- The game may also interpret **analog stick movements** as separate inputs, leading to unintended double actions.

#### **Solution: Using HidHide to Block Unwanted Inputs**
**HidHide** is a tool that allows you to **hide specific USB/HID devices** from being detected by applications. By hiding the problematic PS5 controller components, you can prevent *Star Citizen* from receiving duplicate inputs.

---

### **Step-by-Step Guide to Using HidHide**

#### **1. Download and Install HidHide**
- Download **HidHide** from the official GitHub repository:
  🔗 [https://github.com/ViGEm/HidHide](https://github.com/ViGEm/HidHide)
- Extract the ZIP file and run **HidHideSetup.exe** as Administrator.

#### **2. Identify the Problematic PS5 Controller Devices**
- Open **Device Manager** (`Win + X` > Device Manager).
- Expand **Human Interface Devices (HID)** and look for entries related to your PS5 controller (e.g., "DualSense Wireless Controller").
- Note the **Device Instance Path** (right-click > Properties > Details tab > select "Device Instance Path").

#### **3. Configure HidHide to Hide the Problematic Device**
- Open **HidHide GUI** (run as Administrator).
- Click **Add Rule**.
- In the **Device Instance Path** field, paste the path you noted earlier.
- Under **Process Name**, enter `StarCitizen.exe` (or the exact process name of the game).
- Set **Action** to **Block**.
- Click **OK** and then **Apply Rules**.

#### **4. Test the Fix in Star Citizen**
- Launch *Star Citizen*.
- The PS5 controller should now function normally without double-input issues.

---

### **Alternative Fixes (If HidHide Doesn’t Work)**
1. **Update Star Citizen & Controller Drivers**
   - Ensure both the game and controller drivers are up to date.
2. **Use a Different Input Method**
   - Try remapping controls in-game or using a different controller profile.
3. **Disable Touchpad Input**
   - Some users report disabling the touchpad in the PS5 settings helps.

---

### **Conclusion**
By using **HidHide**, you can block unwanted PS5 controller inputs from being detected by *Star Citizen*, preventing double-input issues. If the problem persists, consider alternative fixes like updating drivers or adjusting in-game settings.

Would you like additional troubleshooting steps if HidHide doesn’t resolve the issue?
