const PDFDocument = require('/home/node/.openclaw/workspace/node_modules/pdfkit');
const fs = require('fs');

// Create output directory if needed
const outputDir = '/home/node/.openclaw/workspace/digital-twins-platform/demo';
if (!fs.existsSync(outputDir)) {
  fs.mkdirSync(outputDir, { recursive: true });
}

// Create PDF document (A4 size)
const doc = new PDFDocument({
  size: 'A4',
  margins: { top: 0, bottom: 0, left: 0, right: 0 }
});

// Output file
const outputPath = `${outputDir}/SimulAI-OnePager.pdf`;
doc.pipe(fs.createWriteStream(outputPath));

// Colors
const darkBlue = '#1a1a2e';
const teal = '#14b8a6';
const indigo = '#6366f1';
const darkText = '#1f2937';
const lightGray = '#f3f4f6';

// Page dimensions (A4: 595.28 x 841.89 points)
const pageWidth = 595.28;
const pageHeight = 841.89;
const margin = 35;
const contentWidth = pageWidth - (margin * 2);

// ===== HEADER =====
doc.rect(0, 0, pageWidth, 85).fill(darkBlue);

// SimulAI logo text
doc.fillColor('#ffffff')
   .fontSize(32)
   .font('Helvetica-Bold')
   .text('SimulAI', margin, 18);

// Tagline
doc.fontSize(11)
   .font('Helvetica-Oblique')
   .text('Simulá el impacto de tus decisiones antes de tomarlas', margin, 52);

// Subtitle
doc.fontSize(9)
   .font('Helvetica')
   .fillColor('#94a3b8')
   .text('Digital Twins + AI Simulation Platform', margin, 68);

// ===== TWO COLUMN SECTION: Problem & Solution =====
const sectionY = 100;
const colWidth = (contentWidth - 20) / 2;
const leftColX = margin;
const rightColX = margin + colWidth + 20;

// Problem Section Header
doc.rect(leftColX, sectionY, colWidth, 22).fill('#fee2e2');
doc.fillColor('#dc2626')
   .fontSize(11)
   .font('Helvetica-Bold')
   .text('THE PROBLEM', leftColX + 8, sectionY + 5);

// Problem content
let probY = sectionY + 30;
doc.fillColor(darkText)
   .fontSize(9)
   .font('Helvetica-Bold')
   .text('Companies lose millions yearly in:', leftColX, probY);

probY += 16;
const problems = [
  '• Unplanned downtime (30-50% of production losses)',
  '• Reactive maintenance (fix when broken, not before)',
  '• Blind decisions (no way to test before executing)'
];

doc.font('Helvetica').fontSize(8);
problems.forEach(p => {
  doc.text(p, leftColX, probY);
  probY += 13;
});

probY += 8;
doc.font('Helvetica-Bold').fontSize(9);
doc.text('Current solutions:', leftColX, probY);
probY += 14;
doc.font('Helvetica').fontSize(8);
doc.fillColor('#dc2626');
doc.text('$100K-$1M+ (Siemens, PTC), months to deploy', leftColX, probY);

// Solution Section Header
doc.fillColor(darkText);
doc.rect(rightColX, sectionY, colWidth, 22).fill('#d1fae5');
doc.fillColor('#059669')
   .fontSize(11)
   .font('Helvetica-Bold')
   .text('THE SOLUTION', rightColX + 8, sectionY + 5);

// Solution content
let solY = sectionY + 30;
doc.fillColor(darkText).fontSize(8).font('Helvetica');
const solutions = [
  { bold: 'Digital twin', text: ' = real-time virtual replica of your operation' },
  { bold: 'AI simulation', text: ' = predict failures, optimize processes, test decisions' },
  { bold: 'Setup in days', text: ', not months' },
  { bold: '10x cheaper', text: ' than enterprise alternatives' }
];

solutions.forEach(s => {
  doc.font('Helvetica-Bold').text(s.bold, rightColX, solY);
  const boldWidth = doc.widthOfString(s.bold);
  doc.font('Helvetica').text(s.text, rightColX + boldWidth, solY);
  solY += 14;
});

// ===== KEY USE CASES =====
const useCasesY = 235;

// Section header bar
doc.rect(margin, useCasesY, contentWidth, 22).fill(teal);
doc.fillColor('#ffffff')
   .fontSize(11)
   .font('Helvetica-Bold')
   .text('KEY USE CASES', margin + 10, useCasesY + 5);

// Use cases in 2x2 grid
const useCases = [
  { icon: '🏭', title: 'Manufacturing', desc: 'Predictive maintenance, production optimization' },
  { icon: '🚚', title: 'Supply Chain', desc: 'Route simulation, distribution optimization' },
  { icon: '⚡', title: 'Energy', desc: 'Generation optimization, demand prediction' },
  { icon: '🏗️', title: 'Infrastructure', desc: 'Real-time building monitoring' }
];

let ucY = useCasesY + 32;
const ucWidth = (contentWidth - 30) / 2;
const uc1X = margin;
const uc2X = margin + ucWidth + 30;

useCases.forEach((uc, i) => {
  const x = i % 2 === 0 ? uc1X : uc2X;
  if (i === 2) ucY += 38;
  
  doc.fillColor(indigo).fontSize(14).text(uc.icon, x, ucY);
  doc.fillColor(darkText).fontSize(9).font('Helvetica-Bold')
     .text(uc.title, x + 22, ucY + 2);
  doc.fontSize(7).font('Helvetica').fillColor('#6b7280')
     .text(uc.desc, x + 22, ucY + 14);
});

// ===== MARKET OPPORTUNITY =====
const marketY = 330;

// Accent bar
doc.rect(margin, marketY, 6, 75).fill(indigo);

doc.fillColor(indigo)
   .fontSize(11)
   .font('Helvetica-Bold')
   .text('MARKET OPPORTUNITY', margin + 15, marketY);

// Big numbers
doc.fontSize(28)
   .font('Helvetica-Bold')
   .fillColor(darkText)
   .text('$21B', margin + 15, marketY + 20);

doc.fontSize(12)
   .font('Helvetica')
   .fillColor('#6b7280')
   .text('(2025)', margin + 15, marketY + 50);

doc.fontSize(20)
   .fillColor(teal)
   .text('→', margin + 75, marketY + 25);

doc.fontSize(28)
   .font('Helvetica-Bold')
   .fillColor(darkText)
   .text('$150B', margin + 95, marketY + 20);

doc.fontSize(12)
   .font('Helvetica')
   .fillColor('#6b7280')
   .text('(2030)', margin + 95, marketY + 50);

doc.fontSize(14)
   .font('Helvetica-Bold')
   .fillColor(teal)
   .text('48% CAGR', margin + 165, marketY + 30);

// Quote
doc.fontSize(9)
   .font('Helvetica-Oblique')
   .fillColor('#4b5563')
   .text('"Agent AI is saturated. Simulation is the next wave."', margin + 15, marketY + 58);

// ===== COMPETITIVE ADVANTAGE =====
const compY = 420;

doc.rect(margin, compY, contentWidth, 22).fill(indigo);
doc.fillColor('#ffffff')
   .fontSize(11)
   .font('Helvetica-Bold')
   .text('COMPETITIVE ADVANTAGE', margin + 10, compY + 5);

// Table
const tableY = compY + 30;
const col1W = 80;
const col2W = (contentWidth - col1W) / 3;
const rowH = 22;

// Header row
doc.rect(margin, tableY, contentWidth, rowH).fill(lightGray);
doc.fillColor(darkText).fontSize(8).font('Helvetica-Bold');
doc.text('', margin + 5, tableY + 6);
doc.text('SimulAI', margin + col1W + 5, tableY + 6);
doc.text('Siemens', margin + col1W + col2W + 5, tableY + 6);
doc.text('Azure DT', margin + col1W + col2W * 2 + 5, tableY + 6);

// Data rows
const rows = [
  ['Price', '$$', '$$$$', '$$$'],
  ['Setup', 'Days', 'Months', 'Weeks'],
  ['AI Native', '✅', '❌', '❌']
];

let rowY = tableY + rowH;
rows.forEach(row => {
  doc.font('Helvetica').fontSize(8).fillColor(darkText);
  doc.text(row[0], margin + 5, rowY + 6);
  doc.font('Helvetica-Bold').fillColor(teal).text(row[1], margin + col1W + 5, rowY + 6);
  doc.font('Helvetica').fillColor('#6b7280').text(row[2], margin + col1W + col2W + 5, rowY + 6);
  doc.text(row[3], margin + col1W + col2W * 2 + 5, rowY + 6);
  
  // Row separator line
  doc.moveTo(margin, rowY + rowH).lineTo(margin + contentWidth, rowY + rowH).stroke('#e5e7eb');
  rowY += rowH;
});

// Table border
doc.rect(margin, tableY, contentWidth, rowH * 4).stroke('#e5e7eb');

// ===== TECH STACK =====
const techY = tableY + rowH * 4 + 20;

doc.rect(margin, techY, contentWidth, 20).fill('#f1f5f9');
doc.fillColor('#475569')
   .fontSize(8)
   .font('Helvetica-Bold')
   .text('TECH STACK:', margin + 10, techY + 5);

doc.font('Helvetica')
   .fillColor(darkText)
   .text('Eclipse Ditto + FastAPI + React + Three.js + AI/ML', margin + 75, techY + 5);

doc.fillColor(teal)
   .font('Helvetica-Bold')
   .text('| Open Source base', margin + 320, techY + 5);

// ===== FOOTER / CONTACT =====
const footerY = pageHeight - 55;

doc.rect(0, footerY, pageWidth, 55).fill(darkBlue);

doc.fillColor('#ffffff')
   .fontSize(10)
   .font('Helvetica-Bold')
   .text('Franco Schiavone — AI Engineer', margin, footerY + 12);

doc.fontSize(9)
   .font('Helvetica')
   .fillColor('#94a3b8')
   .text('francoaschiavone@gmail.com  |  schiavone.ai', margin, footerY + 28);

// Decorative accent
doc.rect(margin, footerY + 42, 60, 3).fill(teal);

// Finalize PDF
doc.end();

console.log(`✅ PDF generated successfully: ${outputPath}`);

// Verify file was created
setTimeout(() => {
  try {
    const stats = fs.statSync(outputPath);
    console.log(`📄 File size: ${(stats.size / 1024).toFixed(2)} KB`);
  } catch (err) {
    console.error('❌ Error verifying file:', err.message);
  }
}, 500);
