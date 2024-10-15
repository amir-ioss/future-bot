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
} from "./_fun/helpers.js";
import botConfig from "./botConfig.js";
import { useStore } from "./store.jsx";

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
    let hl_ = []; // on trading range
    let lh_ = []; // on trading range
    let hl_temp_ = [];
    let lh_temp_ = [];
    let range_start = 0 // index
    var position_span = 0;
    var edgePrice = 0
    var trailing = false
    var status = []


    // var diff = support[tradingRange]["y1"] - resist[tradingRange]["y1"];
    // var supportResistArea = calculatePercentage(diff, botConfig.S_R_Area);
    // resist[tradingRange]["diff"] = diff;
    // support[tradingRange]["diff"] = diff;

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
      if (index < 2) return
      // if (index < initalRangeStart) return

      let hl = hl_.filter(_ => (_.index + botConfig.leftValueSmall) < index)
      let lh = lh_.filter(_ => (_.index + botConfig.leftValueSmall) < index)
      let hl_last = hl.filter(_ => _.index > range_start)
      let lh_last = lh.filter(_ => _.index > range_start)
      let middle = support[tradingRange]['price'] + (resist[tradingRange]['price'] - support[tradingRange]['price']) / 2
      let hl_temp = hl_temp_.filter(_ => (_.index + botConfig.leftValueSmall) < index);
      let lh_temp = lh_temp_.filter(_ => (_.index + botConfig.leftValueSmall) < index);


      const x = padding + index * candleWidth;
      const yHigh = padding + (1 - (cand.h - minPrice) / priceRange) * chartHeight;
      const yLow = padding + (1 - (cand.l - minPrice) / priceRange) * chartHeight;
      const yOpen = padding + (1 - (cand.o - minPrice) / priceRange) * chartHeight;
      const yClose = padding + (1 - (cand.c - minPrice) / priceRange) * chartHeight;

      const spread = percentageChange(support[tradingRange]?.["price"], resist[tradingRange]["price"]);
      var day = new Date(cand["t"]).getDay();
      var isHolyday = hl.length < 2 || lh.length < 2  // day == 5 || day == 6; // SAT, SUN
      // if (isHolyday) Mark(ctx, { x1: x, y1: 30 }, "yellow", 4, 1)

      function ENTRY(type = "LONG", tag = null) {
        if (index < botConfig.leftValueSmall || isHolyday) return
        if (isOrderPlaced) return
        positionTmp["entryPrice"] = cand.o;
        positionTmp["x1"] = x;
        positionTmp["y1"] = yOpen;
        positionTmp["type"] = type;
        isOrderPlaced = true;
        Text(ctx, tag ?? type, x, yOpen - 100, 'white');
        _emit(tag)
      }
      function EXIT(tag = null, exitPrice = cand.o) {
        if (!isOrderPlaced) return
        positionTmp["exitPrice"] = exitPrice ;
        positionTmp["x2"] = x;
        positionTmp["y2"] = yOpen;
        positions.push(positionTmp);
        positionTmp = {};
        isOrderPlaced = false;
        position_span = 0;
        tag && Text(ctx, tag, x, yOpen - 120, 'red');
        _emit(tag)
        hl_temp = []
        lh_temp = []

        status = status.filter(_ => !["crossed_down", "crossed_up"].includes(_))
      }



      function _emit(datalog) {
        if (!datalog) return
        if (index > logStartIndex) {
          setEvent({ index, log: datalog })
        }
      }

   
      // S & R
      Mark(ctx, priceCandle(resistBoxEnd, index), upColor + 40, candleWidth, 1);
      Mark(ctx, priceCandle(resistBoxStart, index), upColor + 90, candleWidth, 1);
      Mark(ctx, priceCandle(supportBoxStart, index), downColor + 90, candleWidth, 1);
      Mark(ctx, priceCandle(supportBoxEnd, index), downColor + 40, candleWidth, 1);
      Mark(ctx, priceCandle(middle, index), '#cccccc10', candleWidth, 1);

      // drawRect(ctx, { x1: x, y1: resistBoxStart, w: 10, h: resistBoxEnd-resistBoxStart }, upColor+20);

      // breakout
      if (breakout == 'bullish') Mark(ctx, { x1: x, y1: 30 }, "#00ff00", 4, 1)
      if (breakout == 'bearish') Mark(ctx, { x1: x, y1: 30 }, "#ff0000", 4, 1)
      if (breakout == 'await') Mark(ctx, { x1: x, y1: 30 }, "#cccccc50", 4, 1)
      edgePrice = edgePrice == 0 ? cand.o : edgePrice // set inital value

      // index == data.length - 1 && console.log(index, range);




      if (breakout == "bearish") {
        edgePrice = cand.o < edgePrice ? cand.o : edgePrice
        let reversed = false
        // let change = percentageChange(supportBoxEnd, edgePrice) // %
        let range = 0

        if (lh_last.length > 0 && hl_last.length > 0) {
          tradingRange += 1
          support[tradingRange] = priceCandle(lh_last.at(-1)?.c, index);
          resist[tradingRange] = priceCandle(hl_last.at(-1)?.c, index);
          // resist[tradingRange] = resist[tradingRange - 1]
          update_support_resist(support[tradingRange]['price'], resist[tradingRange]["price"])
          // Text(ctx, 'new range await', x, 100, 'yellow');
          range += 1
        }



        if (cand.o > support[tradingRange]["price"] && range == 0) {
          EXIT()
          breakout = 'await'
          support[tradingRange] = priceCandle(edgePrice, index)
          resist[tradingRange] = priceCandle(hl.at(-1)?.c, index);
          update_support_resist(support[tradingRange]['price'], resist[tradingRange]["price"])
          Text(ctx, 'new range reverse', x, 100, 'yellow');
          reversed = true
          ENTRY()
        }

        // index == data.length - 1 && console.log(index, range);


        if (cand.o > resistBoxEnd && range != 0) {
          // EDGE
          breakout = 'await'
          const maxHl = hl_last.reduce((max, item) => item.c > max ? item.c : max, -Infinity);
          const maxLh = lh_last.reduce((min, item) => item.c < min ? item.c : min, Infinity);
          tradingRange += 1
          support[tradingRange] = priceCandle(maxLh, index);
          resist[tradingRange] = priceCandle(maxHl, index);
          update_support_resist(support[tradingRange]['price'], resist[tradingRange]["price"])
          Text(ctx, 'new range edge', x, 100, 'yellow');
          EXIT()

        }



      }



      if (breakout == "await") {
        edgePrice = 0

        var reversalCandle = data[index - 1]["o"] > data[index - 1]["c"]  // confirm exit

        var r_b_s_w_p_s = resistBoxStart - calculatePercentage(resistBoxStart - supportBoxStart, position_span * botConfig.targetLoose); // resist_box_start_with_position_span
        isOrderPlaced && positionTmp["type"] == "LONG" && Mark(ctx, priceCandle(r_b_s_w_p_s, index), '#cccccc80', 1, 1);

        var short_r_b_s_w_p_s = supportBoxStart + calculatePercentage(resistBoxStart - supportBoxStart, position_span * botConfig.targetLoose); // resist_box_start_with_position_span
        isOrderPlaced && positionTmp["type"] == "SHORT" && Mark(ctx, priceCandle(short_r_b_s_w_p_s, index), '#cccccc40', 1, 1);


        // LONG ENTRIES 
        if (cand.o < supportBoxStart) {
          // if (cand.o < supportBoxStart || data.at(index - 1).l < supportBoxStart) {
          ENTRY(undefined, 'long')
        } else if ((cand.o > resistBoxStart || data[index - 1].h > resistBoxStart) && positionTmp["type"] == 'LONG') {
          EXIT('exit long', resistBoxStart)
        }


        // SHORT ENTRIES 
        // if (cand.o > resistBoxStart || data.at(index - 1).h > resistBoxStart) {
        if (cand.o > resistBoxStart) {
          ENTRY('SHORT')
        } else if ((cand.o < supportBoxStart || data[index - 1].l < supportBoxStart) && positionTmp["type"] == 'SHORT') {
          EXIT('exit  short, ' + positionTmp["type"], supportBoxStart)

        }


        // ////////////////////////////////////////// special entry exits  //////////////////////////////////////////
        if (positionTmp["type"] == 'SHORT') {
          if (cand.o > lh.at(-1)?.c && cand.o < short_r_b_s_w_p_s) {
            EXIT('exit short, ' + positionTmp["type"])
            Text(ctx, "o > lh", x, priceCandle(edgePrice, index)['y1'], 'yellow');
            ENTRY()
          }

          // if (cand.o < middle) {
          //   status.push('crossed_down')
          // }

          // if (status.includes('crossed_down') && cand.o > middle && cand.o > lh.at(-1)?.c) {
          //   Text(ctx, "o", x, 200, 'yellow');
          //   EXIT('exit short')
          // }

        }


        if (positionTmp["type"] == 'LONG') {
          if (cand.o < hl.at(-1)?.c && cand.o < lh.at(-1)?.c && cand.o > r_b_s_w_p_s) {
            // EXIT('exit long, ' + positionTmp["type"])
            Text(ctx, "o < hl", x, priceCandle(edgePrice, index)['y1'], 'yellow');
            // ENTRY('SHORT')
          }

          // if (cand.o > middle) {
          //   status.push('crossed_up')

          // }
          // if (status.includes('crossed_up') && cand.o < middle && cand.o < hl.at(-1)?.c) {
          //   EXIT('exit long, ' + positionTmp["type"])

          //   Text(ctx, "o", x, priceCandle(edgePrice, index)['y1'], 'yellow');
          // }


        }

        // RETEST

        if (lh.at(-1)?.c > supportBoxStart && lh.at(-2)?.c > supportBoxStart) {
          // Text(ctx, "O", x, priceCandle(cand.o, index)['y1'], 'yellow');
          // resist[tradingRange] = priceCandle(resist[tradingRange]["price"])
          // support[tradingRange] = priceCandle(lh.at(-2)?.c)
          // update_support_resist(support[tradingRange]["price"], resist[tradingRange]["price"])
        }




      }



      if (breakout == "bullish") {
        // status.push('freeze')
        edgePrice = cand.o > edgePrice ? cand.o : edgePrice
        let range = 0

        if (hl_last.length > 0 && lh_last.length > 0) {
          // console.log(priceCandle(hl_last.at(-1)?.c, index), "works---------", priceCandle(lh_last.at(-1)?.c, index));
          tradingRange += 1
          let lastHl = hl_last.at(-1)?.c
          resist[tradingRange] = priceCandle(lastHl < edgePrice ? edgePrice : lastHl, index);
          support[tradingRange] = priceCandle(lh_last.at(-1)?.c, index);
          update_support_resist(support[tradingRange]['price'], resist[tradingRange]['price'])
          // Text(ctx, 'new range await 2', x, 100, 'yellow');
        }



        if (cand.o < resist[tradingRange]["price"] && range == 0) {
          breakout = 'await'
          EXIT(undefined, resist[tradingRange]["price"])

          Text(ctx, 'R', x, 120, 'yellow');
          ENTRY("SHORT")
        }

        if (cand.o < supportBoxEnd && range != 0) {
          // EDGE
          breakout = 'await'
          const maxHl = hl_last.reduce((max, item) => item.c > max ? item.c : max, -Infinity);
          const maxLh = lh_last.reduce((min, item) => item.c < min ? item.c : min, Infinity);
          tradingRange += 1
          support[tradingRange] = priceCandle(maxLh, index);
          resist[tradingRange] = priceCandle(maxHl, index);
          update_support_resist(support[tradingRange]['price'], resist[tradingRange]["price"])
          Text(ctx, 'bullish edge', x, 100, 'yellow');
          EXIT()
        }

      }




      let brk_bearish_change = percentageChange(supportBoxEnd, cand.o) // %
      if (cand.o < supportBoxEnd && breakout == 'await') {
        _emit('BEARISH breakout');
        breakout = "bearish"
        range_start = index
        Text(ctx, 'bearish', x, priceCandle(lh_last.at(-1)?.c, index)['y1'], 'yellow');

        if (positionTmp["type"] != "SHORT") {
          EXIT('on brk', supportBoxEnd)
          if (hl_temp.length == 0 || hl_temp.at(-1)?.c < middle) ENTRY('SHORT', 'breakout S')

        }
      }


      let brk_bullish_change = percentageChange(resistBoxEnd, cand.o) // %

      if (cand.o > resistBoxEnd && breakout == 'await') {
        _emit('BULLISH breakout');
        breakout = "bullish"
        range_start = index
        Text(ctx, 'bullish', x, priceCandle(lh_last.at(-1)?.c, index)['y1'], 'yellow');

        if (positionTmp["type"] != "LONG") {
          EXIT('on brk', resistBoxEnd)
          if (lh_temp.length == 0 || lh_temp.at(-1)?.c > middle) ENTRY(undefined, 'breakout L')
        }

      }



      // logic










      // BULLISH





      // BEARISH



      // trade




















      if (isOrderPlaced) position_span += 1;




      // // High Low shadow
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
        hl_.push({ index, x, yClose, ...cand }); // 🔴
        hl_temp.push({ index, x, yClose, ...cand });
      }
      // LH 10
      if (lhs[index]) {
        ctx.fillStyle = downColor;
        ctx.fillRect(x, yClose, 15, 15);
        lh_.push({ index, x, yClose, ...cand }); // 🔴
        lh_temp.push({ index, x, yClose, ...cand });
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
    }); // END CANDLE LOOP

    // DRAW SUPPORT & RESIST
    0 && support.forEach((s_or_r, idx) => {
      // Initial Resist
      drawTrendLineObj(ctx, support[idx], downColor);
      // Initial Support
      drawTrendLineObj(ctx, resist[idx], upColor);
      // log(support[idx]);
    });

    // DRAW POSITIONS
    // drawTrendLine(ctx, draw);
    var pnl = 0;
    positions.forEach((position, idx) => {
      // if (position["type"] == "LONG") {
      drawPosition(ctx, position, position["type"]);

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