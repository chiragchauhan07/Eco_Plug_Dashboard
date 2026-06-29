const fs = require('fs');
const path = require('path');

function convertHtmlToReact(html) {
  // Extract <main> content
  const mainMatch = html.match(/<main[^>]*>([\s\S]*?)<\/main>/i);
  if (!mainMatch) return null;
  
  let jsx = `<main className="flex-1 p-lg md:p-xl overflow-y-auto max-w-7xl mx-auto w-full">\n${mainMatch[1]}\n</main>`;
  
  // Basic JSX conversions
  jsx = jsx.replace(/class=/g, 'className=');
  jsx = jsx.replace(/for=/g, 'htmlFor=');
  jsx = jsx.replace(/<!--([\s\S]*?)-->/g, '{/* $1 */}');
  
  // Self closing tags
  jsx = jsx.replace(/<img([^>]+[^\/])>/g, '<img$1 />');
  jsx = jsx.replace(/<input([^>]+[^\/])>/g, '<input$1 />');
  jsx = jsx.replace(/<br>/g, '<br />');
  jsx = jsx.replace(/<hr([^>]+[^\/])?>/g, '<hr$1 />');

  // Fix inline styles
  jsx = jsx.replace(/style="font-variation-settings:\s*'FILL'\s*1;?"/g, "style={{ fontVariationSettings: \"'FILL' 1\" }}");
  jsx = jsx.replace(/style="width:\s*([^"]+)"/g, "style={{ width: '$1' }}");
  jsx = jsx.replace(/style="height:\s*([^"]+)"/g, "style={{ height: '$1' }}");
  jsx = jsx.replace(/style="background-color:\s*([^"]+)"/g, "style={{ backgroundColor: '$1' }}");

  return jsx;
}

const stepsDir = 'C:\\Users\\LENOVO\\.gemini\\antigravity-ide\\brain\\b5e482af-7003-40f2-8922-b1ad5cca9caa\\.system_generated\\steps';
const frontendSrc = 'C:\\Users\\LENOVO\\OneDrive\\Documents\\EcoPlug_Dashboard\\frontend\\src\\pages';

const pages = [
  { step: '1369', name: 'DashboardPage' },
  { step: '1370', name: 'FeedbackPage' },
  { step: '1371', name: 'ComplaintsPage' },
  { step: '1372', name: 'AnalyticsPage' },
];

if (!fs.existsSync(frontendSrc)) {
  fs.mkdirSync(frontendSrc, { recursive: true });
}

pages.forEach(page => {
  const contentFile = path.join(stepsDir, page.step, 'content.md');
  if (fs.existsSync(contentFile)) {
    const html = fs.readFileSync(contentFile, 'utf8');
    const jsxContent = convertHtmlToReact(html);
    if (jsxContent) {
      const tsx = `import React from 'react';\n\nexport function ${page.name}() {\n  return (\n    ${jsxContent.split('\\n').join('\\n    ')}\n  );\n}\n`;
      fs.writeFileSync(path.join(frontendSrc, `${page.name}.tsx`), tsx);
      console.log(`Created ${page.name}.tsx`);
    } else {
      console.log(`Failed to extract main tag for ${page.name}`);
    }
  } else {
    console.log(`File not found: ${contentFile}`);
  }
});
