const http = require('http');
const fs = require('fs');
const html = fs.readFileSync('/home/node/.openclaw/workspace/digital-twins-platform/demo/pitch-page.html', 'utf-8');
http.createServer((req, res) => {
  res.writeHead(200, {'Content-Type': 'text/html; charset=utf-8'});
  res.end(html);
}).listen(3456, '0.0.0.0', () => console.log('READY'));
