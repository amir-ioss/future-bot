// Draw
function drawLine(ctx, x1, y1, x2, y2, stroke = "black", width = 3) {
    ctx.beginPath();
    ctx.moveTo(x1, y1);
    ctx.lineTo(x2, y2);
    ctx.strokeStyle = stroke;
    ctx.lineWidth = width;
    ctx.stroke();
  }
  
  function drawRect(ctx, x, y, w, h, stroke = "black", width = 3) {
    ctx.beginPath();
    ctx.lineWidth = width;
    ctx.strokeStyle = stroke;
    ctx.rect(x, y, w, h);
    ctx.stroke();
  }
  
  // CAlC
  
  function nextLineEndpoint(x1, y1, x2, y2) {
    const x3 = x2 + (x2 - x1);
    const y3 = y2 + (y2 - y1);
    return { x: x3, y: y3 };
  }
  
  function calculatePercentage(value, percentage) {
    return (value * percentage) / 100;
  }
  
  export { nextLineEndpoint, drawLine, drawRect, calculatePercentage };
  