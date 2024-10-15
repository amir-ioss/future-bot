import botConfig from "../botConfig";
import { calculatePercentage } from "./helpers";
// https://unicode.org/charts/nameslist/n_2190.html

const drawTrendLineObj = (ctx, obj, color = "blue") => {
  // Support Resist
  ctx.beginPath();
  ctx.moveTo(obj.x1, obj.y1);
  ctx.lineTo(obj.x2, obj.y2);
  ctx.strokeStyle = color;
  ctx.stroke();

  // Support Resist Area
  const supportResistArea = calculatePercentage(obj.diff, botConfig.S_R_Area);
  ctx.fillStyle = color + "20";
  ctx.fillRect(
    obj.x1,
    obj.y1 - supportResistArea / 2,
    obj.x2 - obj.x1,
    supportResistArea
  );
};

const drawPosition = (ctx, draw, type = "LONG") => {
  ctx.beginPath();
  ctx.setLineDash([]);
  ctx.moveTo(draw.x1, draw.y1);
  ctx.lineTo(draw.x2, draw.y2);
  ctx.strokeStyle =
    draw.y1 < draw.y2
      ? type == "LONG"
        ? "red"
        : "green"
      : type == "LONG"
      ? "green"
      : "red"; // "#6f03fc";
  ctx.lineWidth = 3;
  ctx.stroke();
  ctx.lineWidth = 1;
};

const drawTrendLine = (ctx, draw, color = "blue") => {
  ctx.beginPath();
  ctx.moveTo(draw[0], draw[1]);
  ctx.lineTo(draw[2], draw[3]);
  ctx.strokeStyle = color;
  ctx.stroke();
};

const drawLine = (ctx, x1, y1, x2, y2, color = "blue", dash = null) => {
  ctx.beginPath();
  if (dash) ctx.setLineDash(dash);
  else ctx.setLineDash([]);
  ctx.moveTo(x1, y1);
  ctx.lineTo(x2, y2);
  ctx.strokeStyle = color;
  ctx.stroke();
};

const Mark = (ctx, obj, color = "#6f03fc", width = 10, height = 10) => {
  // ctx.fillStyle = color + "20";
  ctx.fillStyle = color;
  ctx.fillRect(obj.x1, obj.y1, width, height);
};

const drawRect = (ctx, obj, color = "blue") => {
  ctx.fillStyle = color + "20";
  ctx.fillRect(obj.x1, obj.y1, obj.w, obj.h);
};

// const Text = (ctx, text = "no text", obj, color = "#fff") => {
//   ctx.fillStyle = color;
//   ctx.fillText(text, obj.x1, obj.y1);
// };

const Text = (
  ctx,
  text = "no text",
  x,
  y,
  color = "#fff",
  font = "12px Arial"
) => {
  ctx.font = font;
  ctx.fillStyle = color;
  ctx.fillText(text, x, y);
};

const icons = {
  bullish: "/icons/bullish.png",
  bearish: "/icons/bearish.png",
  retest: "/icons/retest.png",
  reverse: "/icons/reverse.png",
  return: "/icons/return.png",
};

const image = (ctx, src = "bullish", x = 0, y = 0, w = 30, h = 30) => {
  var img = new Image();
  img.onload = function () {
    ctx.drawImage(img, x, y, w, h); // Or at whatever offset you like
  };
  img.src = icons[src];
};

function getMonthName(monthNumber) {
  const monthNames = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
  ];
  
  return monthNames[monthNumber];  // monthNumber should be between 0 and 11
}


export {
  drawPosition,
  drawTrendLineObj,
  drawTrendLine,
  drawRect,
  Mark,
  Text,
  image,
  drawLine,
  getMonthName
};
