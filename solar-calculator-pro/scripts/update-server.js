#!/usr/bin/env node

/**
 * Simple Update Server for Development
 * 
 * This is a simple HTTP server that serves update files for testing
 * the auto-update functionality during development.
 * 
 * Usage:
 *   node scripts/update-server.js --port 3000 --dir ./release
 */

const http = require('http');
const fs = require('fs');
const path = require('path');
const url = require('url');

// Parse command line arguments
const args = process.argv.slice(2);
const options = {};

for (let i = 0; i < args.length; i += 2) {
  const key = args[i].replace('--', '');
  const value = args[i + 1];
  options[key] = value;
}

const {
  port = 3000,
  dir = './release',
  host = 'localhost'
} = options;

const updateDir = path.resolve(dir);

// MIME types
const mimeTypes = {
  '.yml': 'text/yaml',
  '.json': 'application/json',
  '.exe': 'application/octet-stream',
  '.dmg': 'application/octet-stream',
  '.AppImage': 'application/octet-stream',
  '.deb': 'application/octet-stream',
  '.zip': 'application/zip',
  '.blockmap': 'application/octet-stream'
};

/**
 * Get MIME type for file
 * @param {string} filePath - File path
 * @returns {string} MIME type
 */
function getMimeType(filePath) {
  const ext = path.extname(filePath).toLowerCase();
  return mimeTypes[ext] || 'application/octet-stream';
}

/**
 * Serve file
 * @param {http.ServerResponse} res - Response object
 * @param {string} filePath - File path
 */
function serveFile(res, filePath) {
  fs.stat(filePath, (err, stats) => {
    if (err) {
      res.writeHead(404, { 'Content-Type': 'text/plain' });
      res.end('File not found');
      return;
    }

    const mimeType = getMimeType(filePath);
    const headers = {
      'Content-Type': mimeType,
      'Content-Length': stats.size,
      'Accept-Ranges': 'bytes',
      'Access-Control-Allow-Origin': '*'
    };

    res.writeHead(200, headers);
    const stream = fs.createReadStream(filePath);
    stream.pipe(res);
  });
}

/**
 * List directory contents
 * @param {http.ServerResponse} res - Response object
 * @param {string} dirPath - Directory path
 * @param {string} urlPath - URL path
 */
function listDirectory(res, dirPath, urlPath) {
  fs.readdir(dirPath, { withFileTypes: true }, (err, entries) => {
    if (err) {
      res.writeHead(500, { 'Content-Type': 'text/plain' });
      res.end('Error reading directory');
      return;
    }

    const html = `
<!DOCTYPE html>
<html>
<head>
  <title>Update Server - ${urlPath}</title>
  <style>
    body {
      font-family: Arial, sans-serif;
      max-width: 1200px;
      margin: 0 auto;
      padding: 20px;
      background: #f5f5f5;
    }
    h1 {
      color: #333;
      border-bottom: 2px solid #007bff;
      padding-bottom: 10px;
    }
    .file-list {
      background: white;
      border-radius: 8px;
      padding: 20px;
      box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .file-item {
      padding: 10px;
      border-bottom: 1px solid #eee;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    .file-item:hover {
      background: #f8f9fa;
    }
    .file-item:last-child {
      border-bottom: none;
    }
    .file-name {
      font-weight: 500;
      color: #007bff;
      text-decoration: none;
    }
    .file-name:hover {
      text-decoration: underline;
    }
    .file-size {
      color: #666;
      font-size: 0.9em;
    }
    .directory {
      color: #28a745;
    }
    .back-link {
      display: inline-block;
      margin-bottom: 20px;
      color: #007bff;
      text-decoration: none;
    }
    .back-link:hover {
      text-decoration: underline;
    }
  </style>
</head>
<body>
  <h1>📦 Update Server</h1>
  ${urlPath !== '/' ? `<a href=".." class="back-link">← Back</a>` : ''}
  <div class="file-list">
    <h2>Directory: ${urlPath}</h2>
    ${entries.map(entry => {
      const isDir = entry.isDirectory();
      const icon = isDir ? '📁' : '📄';
      const className = isDir ? 'directory' : '';
      const href = path.join(urlPath, entry.name);
      
      let sizeInfo = '';
      if (!isDir) {
        try {
          const stats = fs.statSync(path.join(dirPath, entry.name));
          const sizeMB = (stats.size / 1024 / 1024).toFixed(2);
          sizeInfo = `<span class="file-size">${sizeMB} MB</span>`;
        } catch (e) {
          sizeInfo = '<span class="file-size">-</span>';
        }
      }
      
      return `
        <div class="file-item">
          <a href="${href}" class="file-name ${className}">
            ${icon} ${entry.name}
          </a>
          ${sizeInfo}
        </div>
      `;
    }).join('')}
  </div>
  <p style="margin-top: 20px; color: #666; text-align: center;">
    Update Server running on http://${host}:${port}
  </p>
</body>
</html>
    `;

    res.writeHead(200, { 'Content-Type': 'text/html' });
    res.end(html);
  });
}

/**
 * Request handler
 * @param {http.IncomingMessage} req - Request object
 * @param {http.ServerResponse} res - Response object
 */
function handleRequest(req, res) {
  const parsedUrl = url.parse(req.url);
  let pathname = parsedUrl.pathname;

  // Remove leading slash and decode
  pathname = decodeURIComponent(pathname.substring(1));

  // Prevent directory traversal
  if (pathname.includes('..')) {
    res.writeHead(403, { 'Content-Type': 'text/plain' });
    res.end('Forbidden');
    return;
  }

  const filePath = path.join(updateDir, pathname);

  console.log(`${req.method} ${req.url} -> ${filePath}`);

  // Check if path exists
  fs.stat(filePath, (err, stats) => {
    if (err) {
      res.writeHead(404, { 'Content-Type': 'text/plain' });
      res.end('Not found');
      return;
    }

    if (stats.isDirectory()) {
      // List directory
      listDirectory(res, filePath, pathname || '/');
    } else {
      // Serve file
      serveFile(res, filePath);
    }
  });
}

/**
 * Start server
 */
function startServer() {
  // Check if update directory exists
  if (!fs.existsSync(updateDir)) {
    console.error(`Error: Update directory does not exist: ${updateDir}`);
    console.error('Please create the directory or specify a different path with --dir');
    process.exit(1);
  }

  const server = http.createServer(handleRequest);

  server.listen(port, host, () => {
    console.log('='.repeat(60));
    console.log('Update Server Started');
    console.log('='.repeat(60));
    console.log(`Server: http://${host}:${port}`);
    console.log(`Directory: ${updateDir}`);
    console.log('='.repeat(60));
    console.log('\nAvailable files:');
    
    try {
      const files = fs.readdirSync(updateDir);
      if (files.length === 0) {
        console.log('  (no files)');
      } else {
        files.forEach(file => {
          const filePath = path.join(updateDir, file);
          const stats = fs.statSync(filePath);
          const type = stats.isDirectory() ? 'DIR' : 'FILE';
          const size = stats.isDirectory() ? '' : ` (${(stats.size / 1024 / 1024).toFixed(2)} MB)`;
          console.log(`  [${type}] ${file}${size}`);
        });
      }
    } catch (e) {
      console.log('  Error reading directory');
    }
    
    console.log('='.repeat(60));
    console.log('\nPress Ctrl+C to stop the server');
  });

  server.on('error', (err) => {
    if (err.code === 'EADDRINUSE') {
      console.error(`Error: Port ${port} is already in use`);
      console.error('Please specify a different port with --port');
    } else {
      console.error('Server error:', err);
    }
    process.exit(1);
  });
}

// Start server if called directly
if (require.main === module) {
  startServer();
}

module.exports = {
  startServer,
  handleRequest
};
