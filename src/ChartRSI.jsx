import React, { useEffect, useRef, useState } from "react";
import {
  drawTrendLine,
  drawTrendLineObj,
  drawPosition,
  drawRect,
  Mark,
  Text
} from "./_fun/draw.js";
import {
  calculatePercentage,
  percentageChange,
  calculateFee,
  log,
  calculateRSI,
  calculateRSIMA
} from "./_fun/helpers.js";
import botConfig from "./botConfig.js";
import { useStore } from "./store.jsx";

const upColor = "#089981";
const downColor = "#f23645";
const bgColor = "#161a25";
const logStartIndex = 0

const candleWidth = 10;
const padding = 5;


const CustomCandlestickChart = ({
  data,
  hhs,
  lls,
  hls,
  lhs,
  initalRangeStart,
  initialResist,
  initialSupport,
  closes
}) => {
  const canvasRef = useRef(null);
  const { setActiveCand, setEvent } = useStore()


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
    const priceCandle = (price, x) => ({
      price,
      x1: padding + x * candleWidth,
      y1: padding + (1 - (price - minPrice) / priceRange) * chartHeight,
      x2: padding + numDatacands * candleWidth,
      y2: padding + (1 - (price - minPrice) / priceRange) * chartHeight,
    });

    var resist = [priceCandle(initialResist, initalRangeStart)];
    var support = [priceCandle(initialSupport, initalRangeStart)];

    // S T R A T E G Y   V A R S
    let hh = [];
    let ll = [];
    let positions = [];
    let isOrderPlaced = false;
    let positionTmp = {};
    let tradingRange = 0;
    let breakout = "await";
    let hl = []; // on trading range
    let lh = []; // on trading range
    var hlOffset = 0;
    var lhOffset = 0;
    var hlOffsetRange = 0;
    var lhOffsetRange = 0;
    var position_span = 0;
    var edgePrice = 0
    var trailing = false
    let lastX = 0


    var diff = support[tradingRange]["y1"] - resist[tradingRange]["y1"];
    var supportResistArea = calculatePercentage(diff, botConfig.S_R_Area);
    resist[tradingRange]["diff"] = diff;
    support[tradingRange]["diff"] = diff;

    // var resistBoxStart_plot = resist[tradingRange]["y1"] + supportResistArea / 2;
    // var resistBoxEnd_plot = resist[tradingRange]["y1"] - supportResistArea / 2;
    // var supportBoxStart_plot = support[tradingRange]["y1"] - supportResistArea / 2;
    // var supportBoxEnd_plot = support[tradingRange]["y1"] + supportResistArea / 2;

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
    }


    // const prices = data.map(_ => _.o)

    // Draw the candlestick chart
    data.forEach((cand, index) => {
      if (index < initalRangeStart) return

      const x = padding + index * candleWidth;
      const yHigh = padding + (1 - (cand.h - minPrice) / priceRange) * chartHeight;
      const yLow = padding + (1 - (cand.l - minPrice) / priceRange) * chartHeight;
      const yOpen = padding + (1 - (cand.o - minPrice) / priceRange) * chartHeight;
      const yClose = padding + (1 - (cand.c - minPrice) / priceRange) * chartHeight;

      const spread = percentageChange(support[tradingRange]?.["price"], resist[tradingRange]["price"]);

      function ENTRY(type = "LONG", tag = null) {

        if (isOrderPlaced) return
        positionTmp["entryPrice"] = cand.o;
        positionTmp["x1"] = x;
        positionTmp["y1"] = yOpen;
        positionTmp["type"] = type;
        isOrderPlaced = true;
        Text(ctx, tag ?? type, x, yOpen - 100, 'white');
        _emit(tag)
      }
      function EXIT(tag = null) {
        if (!isOrderPlaced) return
        positionTmp["exitPrice"] = cand.o;
        positionTmp["x2"] = x;
        positionTmp["y2"] = yOpen;
        positions.push(positionTmp);
        positionTmp = {};
        isOrderPlaced = false;
        position_span = 0;
        // Text(ctx, "EXIT", x, yOpen - 100, 'white');
        _emit(tag)
      }



      function _emit(datalog) {
        if (!datalog) return
        if (index > logStartIndex) {
          setEvent({ index, log: datalog })
        }
      }

      var day = new Date(cand["t"]).getDay();
      var isHolyday = false // day == 5 || day == 6; // SAT, SUN
      // if (isHolyday) Mark(ctx, { x1: x, y1: 30 }, "yellow", 4, 1)
      const RSI = calculateRSI(closes, botConfig.leftValueSmall)
      const RSI_SMA = calculateRSIMA(RSI, botConfig.leftValueSmall)
      console.log(index, RSI[index], RSI_SMA[index]);
      if( RSI_SMA[index] > RSI[index])Mark(ctx, { x1: x, y1: 100, w: 10, h: 10 }, 'pink', candleWidth, 1);


      // S & R
      Mark(ctx, priceCandle(resistBoxEnd, index), upColor + 40, candleWidth, 1);
      Mark(ctx, priceCandle(resistBoxStart, index), upColor + 90, candleWidth, 1);
      Mark(ctx, priceCandle(supportBoxStart, index), downColor + 90, candleWidth, 1);
      Mark(ctx, priceCandle(supportBoxEnd, index), downColor + 40, candleWidth, 1);

      // drawRect(ctx, { x1: x, y1: resistBoxStart, w: 10, h: resistBoxEnd-resistBoxStart }, upColor+20);

      // breakout
      if (breakout == 'bullish') Mark(ctx, { x1: x, y1: 30 }, "#00ff00", 4, 1)
      if (breakout == 'bearish') Mark(ctx, { x1: x, y1: 30 }, "#ff0000", 4, 1)
      if (breakout == 'await') Mark(ctx, { x1: x, y1: 30 }, "#cccccc50", 4, 1)
      edgePrice = edgePrice == 0 ? cand.o : edgePrice // set inital value


      if (breakout == "bearish") {
        edgePrice = cand.o < edgePrice ? cand.o : edgePrice
        let reversed = false
        let change = percentageChange(supportBoxEnd, edgePrice) // %


        // REVERSAL
        if (cand.o > support[tradingRange]["price"]) {
          if (Math.abs(change) < spread) {
            support[tradingRange] = priceCandle(edgePrice, index);
            // UPDATE Support 
            update_support_resist(support[tradingRange]["price"], resist[tradingRange]["price"])
          }
          reversed = true
          breakout = 'await'
          lh = []
          hl = []
          _emit("REVERSED")
          EXIT()
          Mark(ctx, priceCandle(supportBoxEnd, index), 'yellow', candleWidth, candleWidth);
          Text(ctx, change.toFixed(1) + '%', x, priceCandle(edgePrice, index)['y1'], 'yellow');
          ENTRY()
        }
        // hl > lh || lh > lh-1 
        if (lhOffsetRange > botConfig.leftValueSmall &&
          ((hlOffsetRange > botConfig.leftValueSmall && hl.at(-1)?.c > lh.at(-1)?.c) || lh.at(-1)?.c > lh.at(-2)?.c) &&
          !reversed
        ) {
          Mark(ctx, priceCandle(supportBoxEnd, index), 'MediumPurple', 10, 10);
          tradingRange += 1

          if (Math.abs(change) > spread) {
            resist[tradingRange] = priceCandle(hl.at(-1).c, index);
          } else {
            resist[tradingRange] = priceCandle(support[tradingRange - 1]["price"], index);
          }
          resist[tradingRange] = priceCandle(hl.at(-1).c, index);

          support[tradingRange] = priceCandle(lh.at(-1)?.c, index);
          // UPDATE Support Resist
          update_support_resist(support[tradingRange]["price"], resist[tradingRange]["price"])
          EXIT()
          breakout = 'await'
          lhOffsetRange = 0
          _emit("new range")

          Text(ctx, change.toFixed(1) + '%', x, priceCandle(edgePrice, index)['y1']);
        }

      }



      if (breakout == "await") {
        // if (lh.at(-1)?.c > lh.at(-2)?.c && lhs[index]) {
        //   Text(ctx, '↗', x, priceCandle(cand.o, index)['y1'], 'green', '30px Arial ');
        // }


        // RE-TEST
        // if (hl.at(-1)?.c < hl.at(-2)?.c && !hl.some(_ => _.c > resistBoxStart) && hlOffsetRange == botConfig.leftValueSmall) {
        //   Text(ctx, '↺', x, priceCandle(cand.o, index)['y1'], 'green', '30px Arial ');
        // }
        // if (lh.at(-1)?.c < lh.at(-2)?.c && !lh.some(_ => _.c < supportBoxStart) && lhOffsetRange == botConfig.leftValueSmall) {
        //   Text(ctx, '↺', x, priceCandle(cand.o, index)['y1'], 'red', '30px Arial ');
        // }

        // var reversalCandle = index > 1 ? data[index - 1]["o"] < cand.o : false; // confirm exit
        var reversalCandle = index > 1 ? data[index - 1]["c"] > cand.o : false; // confirm exit



        var r_b_s_w_p_s = resistBoxStart - calculatePercentage(resistBoxStart - supportBoxStart, position_span * botConfig.targetLoose); // resist_box_start_with_position_span
        isOrderPlaced && positionTmp["type"] == "LONG" && Mark(ctx, priceCandle(r_b_s_w_p_s, index), '#cccccc80', 1, 1);

        var short_r_b_s_w_p_s = supportBoxStart + calculatePercentage(resistBoxStart - supportBoxStart, position_span * botConfig.targetLoose); // resist_box_start_with_position_span
        isOrderPlaced && positionTmp["type"] == "SHORT" && Mark(ctx, priceCandle(short_r_b_s_w_p_s, index), '#cccccc40', 1, 1);



        // LONG ENTRIES 
        if (cand.o < supportBoxStart || data.at(index - 1).l < supportBoxStart) {
          ENTRY(undefined, 'long')
        } else if ((cand.o > resistBoxStart || data.at(index - 1).h > resistBoxStart || cand.o > r_b_s_w_p_s || data[index - 1]['h'] > r_b_s_w_p_s) && positionTmp["type"] == 'LONG' && reversalCandle) {
          EXIT('exit long')
          if (cand.o > r_b_s_w_p_s || data[index - 1]['c'] > r_b_s_w_p_s) {
            resist[tradingRange] = priceCandle(cand.o, index);
            update_support_resist(support[tradingRange]["price"], resist[tradingRange]["price"])
          }
        }


        // SHORT ENTRIES 
        if (cand.o > resistBoxStart || data.at(index - 1).h > resistBoxStart) {
          ENTRY('SHORT')
        } else if ((cand.o < supportBoxStart || data.at(index - 1).l < supportBoxStart || cand.o < short_r_b_s_w_p_s || data[index - 1]['l'] < short_r_b_s_w_p_s) && positionTmp["type"] == 'SHORT' && !reversalCandle) {
          EXIT('exit  short, ' + positionTmp["type"])
          if (cand.o < short_r_b_s_w_p_s) {
            support[tradingRange] = priceCandle(cand.o, index);
            update_support_resist(support[tradingRange]["price"], resist[tradingRange]["price"])
          }
        }
        

      }



      if (breakout == "bullish") {
        edgePrice = cand.o > edgePrice ? cand.o : edgePrice
        let reversed = false
        let change = percentageChange(resistBoxEnd, edgePrice) // %


        // REVERSAL
        if (cand.o < resist[tradingRange]["price"]) {
          if (Math.abs(change) < spread) {
            resist[tradingRange] = priceCandle(edgePrice, index);
            // UPDATE Support 
            update_support_resist(support[tradingRange]["price"], resist[tradingRange]["price"])
          }
          reversed = true
          breakout = 'await'
          lh = []
          hl = []
          _emit("REVERSED")
          EXIT()
          Mark(ctx, priceCandle(edgePrice, index), 'yellow', candleWidth, candleWidth);
          Text(ctx, change.toFixed(1) + '%', x, priceCandle(edgePrice, index)['y1'], 'yellow');
          ENTRY('SHORT')
        }

        if (lhOffsetRange > botConfig.leftValueSmall && hlOffsetRange > botConfig.leftValueSmall &&
          hl.at(-1)?.c > lh.at(-1)?.c &&
          !reversed
        ) {
          Mark(ctx, priceCandle(resistBoxEnd, index), 'MediumPurple', 10, 10);
          tradingRange += 1

          if (Math.abs(change) > spread) {
            support[tradingRange] = priceCandle(lh.at(-1).c, index);
            resist[tradingRange] = priceCandle(hl.at(-1).c, index);
          } else {
            support[tradingRange] = priceCandle(resist[tradingRange - 1]["price"], index);
            resist[tradingRange] = priceCandle(edgePrice, index);
          }
          // UPDATE Support Resist
          update_support_resist(support[tradingRange]["price"], resist[tradingRange]["price"])
          EXIT()
          breakout = 'await'
          lhOffsetRange = 0
          _emit("new range")

          Text(ctx, `${change.toFixed(1)}% ${spread}`, x, priceCandle(edgePrice, index)['y1']);
        }

      }





      if (cand.o < supportBoxEnd && breakout == 'await') {
        _emit('BEARISH breakout');
        breakout = "bearish"
        lh = []
        hl = []
        EXIT()
        ENTRY("SHORT", 'breakout short entry')

      }


      if (cand.o > resistBoxEnd && breakout == 'await') {
        _emit('BULLISH breakout');
        breakout = "bullish"
        lh = []
        hl = []
        EXIT()
        ENTRY(undefined, 'breakout long entry')

      }



      // logic










      // BULLISH





      // BEARISH



      // trade





















      // delay hh ll
      if (hls[index]) hlOffset = 1
      if (hlOffset > 0) hlOffset += 1

      if (lhs[index]) lhOffset = 1
      if (lhOffset > 0) lhOffset += 1

      // delay hh ll
      if (hls[index]) hlOffsetRange = 1
      if (hlOffsetRange > 0) hlOffsetRange += 1

      if (lhs[index]) lhOffsetRange = 1
      if (lhOffsetRange > 0) lhOffsetRange += 1

      if (isOrderPlaced) position_span += 1;




      // High Low shadow
      ctx.beginPath();
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
      // HL 10
      if (hls[index]) {
        ctx.fillStyle = upColor;
        ctx.fillRect(x, yClose, 15, 15);
        hl.push({ index, x, yClose, ...cand }); // 🔴
      }
      // LH 10
      if (lhs[index]) {
        ctx.fillStyle = downColor;
        ctx.fillRect(x, yClose, 15, 15);
        lh.push({ index, x, yClose, ...cand }); // 🔴
      }

      // HH
      if (hhs[index]) {
        hh.push({ x, yClose }); // 🔴

        ctx.beginPath();
        ctx.arc(x, yClose, 25, 0, 2 * Math.PI);
        ctx.stroke();
      }
      // LL
      if (lls[index]) {
        ll.push({ x, yClose }); // 🔴

        ctx.beginPath();
        ctx.arc(x, yClose, 25, 0, 2 * Math.PI);
        ctx.stroke();
      }

      // line
      // index == 50 && draw.push(x, yHigh);
      // index == 150 && draw.push(x, yHigh);


      // RSI

      // const RSI = calculateRSI(closes)
      // ctx.beginPath();
      // ctx.moveTo(x, yClose);

      // if (index > 1) {
      //   let line = priceCandle(RSI[index], index)
      //   let linePrev = priceCandle(RSI[index - 1], index - 1)
      //   // drawTrendLineObj(ctx, { x1: linePrev.x1, y1: linePrev.y1, x2: line.x1, y2: line.y1 }, '#fff')

      //   const xc = (line.x1 + linePrev.x1) / 2;
      //   const yc = (line.y1+linePrev.y1) / 2;

      //   ctx.quadraticCurveTo(
      //     lastX,
      //     RSI[index],
      //     // xc,
      //     // yc,
      //     lastX,
      //     RSI[index - 1],
      //   );

      //   ctx.strokeStyle = '#fff';
      //   ctx.stroke();
      //   lastX = x

      // }
      // const lastPointX = x
      // const lastPointY = yClose;
      // ctx.quadraticCurveTo(lastPointX, lastPointY, lastPointX, lastPointY);

    }); // END CANDLE LOOP

    // DRAW SUPPORT & RESIST

    // false && support.forEach((s_or_r, idx) => {
    //   // Initial Resist
    //   drawTrendLineObj(ctx, support[idx], downColor);
    //   // Initial Support
    //   drawTrendLineObj(ctx, resist[idx], upColor);
    //   // log(support[idx]);
    // });

    // DRAW POSITIONS
    // drawTrendLine(ctx, draw);
    var pnl = 0;
    positions.forEach((position, idx) => {
      // if (position["type"] == "LONG") {
      drawPosition(ctx, position, position["type"]);

      // RESULT BOX
      let INVEST = 10; // $60 = Rs-5000
      let LEVERAGE = 10; // x
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
      pnl += pl;

      ctx.font = "16px Arial";
      // entryPrice exitPrice
      ctx.fillStyle = pl < 0 ? "red" : "white";
      ctx.fillText(pl.toFixed(2), 20, (idx + 1) * 30);
      ctx.fillText("(" + diff.toFixed(2) + "%)", 70, (idx + 1) * 30);
      ctx.fillStyle = "#6f03fc";
      ctx.fillText(pnl.toFixed(2), 160, (idx + 1) * 30);
      // }

      // if (position["type"] == "SHORT") {
      //   // log("SHORT", position);
      // }
    });

  };






  useEffect(() => {
    drawCandlestickChart();
  }, [data]);

  return (<>

    <canvas
      ref={canvasRef}
      width={window.innerWidth * 20}
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



// // Draw the smooth closing price line
// context.beginPath();
// context.moveTo(padding + candleWidth / 2, scaleY(candlestickData[0].close));
// for (let i = 1; i < candlestickData.length - 1; i++) {
//   const xc = (padding + i * (candleWidth ) + padding + (i + 1) * (candleWidth )) / 2;
//   const yc = (scaleY(candlestickData[i].close) + scaleY(candlestickData[i + 1].close)) / 2;
//   context.quadraticCurveTo(
//     padding + i * (candleWidth),
//     scaleY(candlestickData[i].close),
//     xc,
//     yc
//   );
// }
// const lastPointX = padding + (candlestickData.length - 1) * (candleWidth);
// const lastPointY = scaleY(candlestickData[candlestickData.length - 1].close);
// context.quadraticCurveTo(lastPointX, lastPointY, lastPointX, lastPointY);
// context.strokeStyle = 'blue';
// context.stroke();

