// <!-- B2-23 START -->
const { app, BrowserWindow, shell } = require('electron');
const path = require('path');
const { spawn } = require('child_process');

const PYTHON = 'C:\\Users\\jscot\\AppData\\Local\\Python\\pythoncore-3.14-64\\python.exe';
const PROJECT = path.join(__dirname, '..');
const MCC_SERVER = path.join(PROJECT, 'mcc_server.py');
const PORT = 8080;

let serverProc = null;
let mainWindow = null;

function startServer() {
  serverProc = spawn(PYTHON, [MCC_SERVER], {
    cwd: PROJECT,
    detached: false,
    stdio: 'pipe',
  });
  serverProc.stdout.on('data', d => console.log('[MCC]', d.toString().trim()));
  serverProc.stderr.on('data', d => console.error('[MCC-ERR]', d.toString().trim()));
  serverProc.on('exit', code => console.log('[MCC] Server exited:', code));
}

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    title: 'VKB Spin Doctor — Mission Control',
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
    },
    icon: path.join(PROJECT, 'assets', 'icon.png'),
  });

  // Wait 1.5 s for server to boot then load
  setTimeout(() => {
    mainWindow.loadURL(`http://localhost:${PORT}`);
  }, 1500);

  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    shell.openExternal(url);
    return { action: 'deny' };
  });

  mainWindow.on('closed', () => { mainWindow = null; });
}

app.whenReady().then(() => {
  startServer();
  createWindow();
  app.on('activate', () => { if (BrowserWindow.getAllWindows().length === 0) createWindow(); });
});

app.on('window-all-closed', () => {
  if (serverProc) { serverProc.kill(); serverProc = null; }
  if (process.platform !== 'darwin') app.quit();
});
// <!-- B2-23 END -->
