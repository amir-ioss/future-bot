import React, { useEffect, useRef, useState } from "react";
import {
  drawTrendLine,
  drawTrendLineObj,
  drawPosition,
  drawRect,
  Mark,
  Text,
  image,
  drawLine
} from "./_fun/draw.js";
import {
  calculatePercentage,
  percentageChange,
  calculateFee,
  log,
  calculateRSI,
  transformData
} from "./_fun/helpers.js";
import botConfig from "./botConfig.js";
import { useStore } from "./store.jsx";
import StatusStore from './_fun/StatusStore.js'

// import { isBullishKicker, isBearishKicker, isHammer, isBearishInvertedHammer } from "candlestick"



const upColor = "#089981";
const downColor = "#f23645";
const bgColor = "#161a25";
const logStartIndex = 0

const candleWidth = 6;
const padding = 2;




const CustomCandlestickChart = ({
  data,
  hhs,
  lls,
  hls,
  lhs,
  initalRangeStart,
  initialResist,
  initialSupport,
  hls10,
  lhs10,
  bot
}) => {
  const canvasRef = useRef(null);
  const { setActiveCand, setEvent } = useStore()
  // console.log(bot?.candles);



  const handleMouseMove = (e) => {
    const canvas = canvasRef.current;
    const rect = canvas.getBoundingClientRect();
    const mouseX = e.clientX - rect.left;
    const index = Math.floor(mouseX / (candleWidth - .895)); // Assuming candlestick width is 10px with 5px spacing
    if (data[index]) {
      setActiveCand({ index, cand: data[index], pos: { x: index, y: e.clientY } })
    }
  };

  const handleMouseOut = () => {
    setActiveCand(null);
  };




  const drawCandlestickChart = () => {
    if (!canvasRef.current) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext("2d");
    const canvasBox = canvas.getBoundingClientRect();

    // Clear the canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    // Replace these values with your desired dimensions
    const chartWidth = window.innerWidth;
    const chartHeight = canvasBox.height // window.innerHeight;

    // Calculate candlestick dimensions
    const numDatacands = data.length;
    // const candleWidth = (chartWidth - padding * 2) / numDatacands;
    const maxPrice = Math.max(...data.map((cand) => cand.h));
    const minPrice = Math.min(...data.map((cand) => cand.l));
    const priceRange = maxPrice - minPrice;

    // D R A W   V A R S
    const onChart = (price, x) => ({
      price,
      x1: padding + x * candleWidth,
      y1: padding + (1 - (price - minPrice) / priceRange) * chartHeight,
      x2: padding + numDatacands * candleWidth,
      y2: padding + (1 - (price - minPrice) / priceRange) * chartHeight,
    });

    var resist = [onChart(initialResist, initalRangeStart)];
    var support = [onChart(initialSupport, initalRangeStart)];

    // S T R A T E G Y   V A R S
    let hh = [];
    let ll = [];
    let positions = [];
    let isOrderPlaced = false;
    let positionTmp = {};
    let tradingRange = 0;
    let breakout = "await";
    let hl_ = []; // on trading range
    let lh_ = []; // on trading range
    let hl_temp_ = [];
    let lh_temp_ = [];
    let hl10_ = []
    let lh10_ = []
    let range_start = 0 // index
    var position_span = 0;
    var edgePrice = 0
    var edgePriceUp = 0
    var edgePriceDown = 0
    var trailing = false
    // var status = []
    var Status = new StatusStore()
    var strong_support = false
    var strong_resist = false


    var diff = resist[tradingRange]["price"] - support[tradingRange]["price"];
    var supportResistArea = calculatePercentage(diff, botConfig.S_R_Area);
    var resistBoxStart = resist[tradingRange]["price"] - supportResistArea / 2;
    var resistBoxEnd = resist[tradingRange]["price"] + supportResistArea / 2;
    var supportBoxStart = support[tradingRange]["price"] + supportResistArea / 2;
    var supportBoxEnd = support[tradingRange]["price"] - supportResistArea / 2;

    // ctx.fillRect(500, supportBoxEnd - 5, 10, 10); // position finder

    function update_support_resist(support, resist, invert = false) {
      diff = resist - support
      supportResistArea = calculatePercentage(diff, botConfig.S_R_Area);
      resistBoxStart = resist - supportResistArea / 2;
      resistBoxEnd = resist + supportResistArea / 2;
      supportBoxStart = support + supportResistArea / 2;
      supportBoxEnd = support - supportResistArea / 2;

      Status.remove('bullish')
      Status.remove('bearish')
    }

    // const prices = data.map(_ => _.o)



    // Draw the candlestick chart
    data.forEach((cand, index) => {
      if (index < 1) return
      const end = index == data.length - 1

      const x = padding + index * candleWidth;
      const yHigh = padding + (1 - (cand.h - minPrice) / priceRange) * chartHeight;
      const yLow = padding + (1 - (cand.l - minPrice) / priceRange) * chartHeight;
      const yOpen = padding + (1 - (cand.o - minPrice) / priceRange) * chartHeight;
      const yClose = padding + (1 - (cand.c - minPrice) / priceRange) * chartHeight;



      // S & R
      // Mark(ctx, onChart(resistBoxEnd, index), upColor + 30, candleWidth, onChart(resistBoxStart, index).y1 - onChart(resistBoxEnd, index).y1);
      // Mark(ctx, onChart(supportBoxEnd, index), downColor + 30, candleWidth, onChart(supportBoxStart, index).y1 - onChart(supportBoxEnd, index).y1);

      // Mark(ctx, onChart(resistBoxEnd, index), upColor + 40, candleWidth, 1);
      // Mark(ctx, onChart(resistBoxStart, index), upColor + 90, candleWidth, 1);
      // Mark(ctx, onChart(supportBoxStart, index), downColor + 90, candleWidth, 1);
      // Mark(ctx, onChart(supportBoxEnd, index), downColor + 40, candleWidth, 1);
      // Mark(ctx, onChart(middle, index), '#cccccc10', candleWidth, 1);

      index % 5 == 0 && Text(ctx, index, x, 10, '#cccccc50');
      let isHolyday = false

      // drawRect(ctx, { x1: x, y1: resistBoxStart, w: 10, h: resistBoxEnd-resistBoxStart }, upColor+20);

      // breakout
      if (bot.breakouts[index] == 'bullish') Mark(ctx, { x1: x, y1: 30 }, "#00ff00", 4, 1)
      if (bot.breakouts[index] == 'bearish') Mark(ctx, { x1: x, y1: 30 }, "#ff0000", 4, 1)
      if (bot.breakouts[index] == 'await') Mark(ctx, { x1: x, y1: 30 }, "#cccccc50", 4, 1)
        


      // // High Low shadow
      ctx.beginPath();
      ctx.setLineDash([]);
      ctx.moveTo(x, yHigh);
      ctx.lineTo(x, yLow);
      ctx.strokeStyle = cand.o <= cand.c ? isHolyday ? upColor + 40 : upColor : isHolyday ? downColor + 40 : downColor;
      ctx.stroke();

      // Open Close body
      ctx.fillStyle = cand.o <= cand.c ? isHolyday ? upColor + 40 : upColor : isHolyday ? downColor + 40 : downColor;
      ctx.fillRect(x - 2.5, yOpen, candleWidth - padding, yClose - yOpen);

      // Add text elements
      // ctx.translate(x, 0);
      // ctx.font = "12px Arial";
      // ctx.fillStyle = "#ffffff20";
      // X-axis label
      // ctx.fillText(index, x - 2.5, yOpen - 400);



      // DRAW INDICATORS


      // Function to draw text box and the text
      function drawTextBox(x, y, text, fill) {
        // Clear the canvas
        // ctx.clearRect(0, 0, canvas.width, canvas.height);

        // Draw the text box
        ctx.fillStyle = fill
        ctx.fillRect(x, y, 30, 30);

        // Draw the text
        ctx.font = '16px Arial';
        ctx.fillStyle = '#fff';
        ctx.fillText(text, x, y + 25);
      }
      // drawTextBox(x, yClose, 'LL', 'red');
      


      if (bot['marks']) {
        bot['marks'].map(_ => {
          let { x1: x, y1: y } = onChart(_.price, _.index)
          return image(ctx, _.mark, x, y)
          // return Mark(ctx, onChart(_.price, _.index), 'yellow', 6, 6);
        })
      }


      if (bot['text']) {
        bot['text'].map(_ => {
          let cord = onChart(_.price, _.index)
          return Text(ctx, _.text, cord.x1, cord.y1, _?.color);
          // return Mark(ctx, onChart(_.price, _.index), 'yellow', 6, 6);
        })
      }


      if (bot['h_points'][index]) {
        ctx.beginPath();
        ctx.arc(x, yClose, 6, 0, 2 * Math.PI);
        ctx.stroke();
        ctx.fillStyle = upColor;
        ctx.fill();
      }

      if (bot['l_points'][index]) {
        ctx.beginPath();
        ctx.arc(x, yClose, 6, 0, 2 * Math.PI);
        ctx.stroke();
        ctx.fillStyle = downColor;
        ctx.fill();
      }




      // line
      // index == 50 && draw.push(x, yHigh);
      // index == 150 && draw.push(x, yHigh);
    }); // END CANDLE LOOP

    // DRAW SUPPORT & RESIST
    bot?.resists.forEach((res, idx) => {
      // let ch_1 = onChart(res.price, res.start_index)
      // let ch_2 = onChart(res.price, res.end_index)
      // drawLine(ctx, ch_1.x1, ch_1.y1, res.end_index ? ch_2.x1 : ch_2.x2, ch_2.y1, upColor)


      let hl_top_1 = onChart(res.hl_top, res.start_index)
      let hl_top_2 = onChart(res.hl_top, res.end_index)
      // drawLine(ctx, hl_top_1.x1, hl_top_1.y1, res.end_index ? hl_top_2.x1 : hl_top_2.x2, hl_top_2.y1, res?.breakout == 'await' ? upColor + 60 : 'blue')

      let hl_bot_1 = onChart(res.hl_bot, res.start_index)
      // let hl_bot_2 = onChart(res.hl_bot, res.end_index)
      // drawLine(ctx, hl_bot_1.x1, hl_bot_1.y1, res.end_index ? hl_bot_2.x1 : hl_bot_2.x2, hl_bot_2.y1, res?.breakout == 'await' ? upColor + 60 : 'blue')

      // box draw
      var w = (res.end_index ? hl_top_2.x1 : hl_top_2.x2) - hl_top_1.x1
      var h = hl_bot_1.y1 - hl_top_1.y1 
      ctx.fillStyle = res?.breakout == 'await' ? upColor + 20 : '#511cff20'
      ctx.fillRect(hl_top_1.x1, hl_top_1.y1, w, h);

    });

    bot?.supports.forEach((sup, idx) => {
      // let ch_1 = onChart(sup.price, sup.start_index)
      // let ch_2 = onChart(sup.price, sup.end_index)
      // drawLine(ctx, ch_1.x1, ch_1.y1, sup.end_index ? ch_2.x1 : ch_2.x2, ch_2.y1, downColor)

      let lh_top_1 = onChart(sup.lh_top, sup.start_index)
      let lh_top_2 = onChart(sup.lh_top, sup.end_index)
      // drawLine(ctx, lh_top_1.x1, lh_top_1.y1, sup.end_index ? lh_top_2.x1 : lh_top_2.x2, lh_top_2.y1, sup?.breakout == 'await' ? downColor + 60 : 'blue')

      let lh_bot_1 = onChart(sup.lh_bot, sup.start_index)
      let lh_bot_2 = onChart(sup.lh_bot, sup.end_index)
      // drawLine(ctx, lh_bot_1.x1, lh_bot_1.y1, sup.end_index ? lh_bot_2.x1 : lh_bot_2.x2, lh_bot_2.y1, sup?.breakout == 'await' ? downColor + 60 : 'blue')

      // box draw
      var w = (sup.end_index ? lh_top_2.x1 : lh_top_2.x2) - lh_top_1.x1
      var h = lh_bot_2.y1-lh_top_1.y1
      ctx.fillStyle = sup?.breakout == 'await' ? downColor + 15 : '#ff1c9920'
      ctx.fillRect(lh_top_1.x1, lh_top_1.y1, w, h);

    });


    // STRONG RESISTS
    bot?.strong_resists.forEach((res, idx) => {
      let line1 = onChart(res.price, res.start_index)
      let line2 = onChart(res.price, res.end_index)
      drawLine(ctx, line1.x1, line1.y1, res?.end_index ? line2.x1 : line1.x2, line1.y2, upColor,  [4, 6])
      // drawLine(ctx, line2.x1, line1.y1, line1.x2, line1.y2, '#00FF8C50', [8, 6]) // tail
    });;


    // STRONG SUPPORTS
    bot?.strong_supports.forEach((sup, idx) => {
      let line1 = onChart(sup.price, sup.start_index)
      let line2 = onChart(sup.price, sup.end_index)
      drawLine(ctx, line1.x1, line1.y1, sup?.end_index ? line2.x1 : line1.x2, line1.y2, downColor, [4, 6])
      // drawLine(ctx, line2.x1, line1.y1, line1.x2, line1.y2, '#FF008850', [8, 6]) // tail
    });


    // DRAW POSITIONS
    var pnl = 0;
    bot.positions.forEach((position, idx) => {
      let start = onChart(position.entryPrice, position.startIndex)
      let end = onChart(position.exitPrice, position.endIndex)
      let cord = {
        x1: start.x1,
        y1: start.y1,
        x2: end.x1,
        y2: end.y1
      }
      drawPosition(ctx, cord, position["type"]);

      // RESULT BOX
      let INVEST = 10; // $60 = Rs-5000
      let LEVERAGE = 5; // x
      let FEE = 0.05; // %
      let amount = INVEST / position.entryPrice;
      let exit_size = amount * position.exitPrice;

      // LEVERAGE
      let l_entry_size = INVEST * LEVERAGE;
      let l_exit_size = exit_size * LEVERAGE;

      let amount_entry_fee = calculatePercentage(l_entry_size, FEE);
      let amount_exit_fee = calculatePercentage(l_exit_size, FEE);
      var diff = percentageChange(position.entryPrice, position.exitPrice);
      // const fee_entry = calculateFee(INVEST, LEVERAGE, FEE);
      // const fee_exit = calculateFee(exit_size, LEVERAGE, FEE);

      let pl =
        l_exit_size - l_entry_size - (amount_entry_fee + amount_exit_fee);

      if (position["type"] == "SHORT") {
        pl = l_entry_size - l_exit_size - (amount_entry_fee + amount_exit_fee);
        var diff = percentageChange(position.exitPrice, position.entryPrice);
      }

      // if (pl > 3) return

      pnl += pl;

      ctx.font = "16px Arial";
      // entryPrice exitPrice
      ctx.fillStyle = pl < 0 ? "red" : "white";
      ctx.fillText(pl.toFixed(2), 20, (idx + 1) * 30);
      ctx.fillText("(" + diff.toFixed(2) + "%)", 70, (idx + 1) * 30);
      ctx.fillStyle = "#6f03fc";
      ctx.fillText(pnl.toFixed(2), 160, (idx + 1) * 30);
      console.log({pnl});
    
    });
  };

  useEffect(() => {
    drawCandlestickChart();
  }, [data]);

  return (<>

    <canvas
      ref={canvasRef}
      // width={window.innerWidth * 20}
      width={(candleWidth * data.length) + window.innerWidth / 2}
      height={window.innerHeight}
      style={{
        backgroundColor: bgColor,
      }}
      onMouseMove={handleMouseMove}
      onMouseOut={handleMouseOut}
    />
  </>
  );
};

export default CustomCandlestickChart;