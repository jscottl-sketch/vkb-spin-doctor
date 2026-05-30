   syntax = "proto3";

   enum InputType {
       KEYBOARD = 0;
       JOYSTICK = 1;
   }

   message InputCommand {
       InputType type = 1;
       uint64 code = 2;
       int32 value = 3;
       int64 timestamp = 4;
   }

   message InputState {
       repeated InputCommand active = 1;
   }
   