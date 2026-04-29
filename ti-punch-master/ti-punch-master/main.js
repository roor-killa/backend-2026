// =============================================
//   Ti Punch Master – main.js (Electron)
//   Version 2.0 · Martinique 2026
// =============================================

const { app, BrowserWindow, Menu } = require('electron');
const path = require('path');

function createWindow() {
  const win = new BrowserWindow({
    width: 900,
    height: 700,
    minWidth: 520,
    minHeight: 580,
    title: 'Ti Punch Master',
    backgroundColor: '#c8783a',
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
    },
    icon: path.join(__dirname, 'icon.png'),
  });

  win.loadFile('index.html');

  // Remove default menu bar in production
  if (app.isPackaged) {
    Menu.setApplicationMenu(null);
  }
}

app.whenReady().then(() => {
  createWindow();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit();
});
