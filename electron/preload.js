// <!-- B2-23 START -->
const { contextBridge } = require('electron');

contextBridge.exposeInMainWorld('electronMCC', {
  version: '1.0.0',
  platform: process.platform,
});
// <!-- B2-23 END -->
