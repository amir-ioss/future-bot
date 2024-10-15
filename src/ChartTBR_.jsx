import React, { useEffect, useRef, useState } from "react";
import {
  drawTrendLine,
  drawTrendLineObj,
  drawPosition,
  drawRect,
  Mark,
  Text,
  image
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

import { isBullishKicker, isBearishKicker, isHammer, isBearishInvertedHammer } from "candlestick"



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
  lhs10
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
    let hl10_ = []
    let lh10_ = []
    let range_start = 0 // index
    var position_span = 0;
    var edgePrice = 0
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


      let hl = hl_.filter(_ => (_.index + botConfig.leftValueSmall) < index)
      let lh = lh_.filter(_ => (_.index + botConfig.leftValueSmall) < index)
      let hl10 = hl10_.filter(_ => (_.index + 10) < index)
      let lh10 = lh10_.filter(_ => (_.index + 10) < index)

      let hl_last = hl.filter(_ => _.index > range_start) // breakout area
      let lh_last = lh.filter(_ => _.index > range_start) // breakout area
      let hl_temp = hl_temp_.filter(_ => (_.index + botConfig.leftValueSmall) < index); // position area
      let lh_temp = lh_temp_.filter(_ => (_.index + botConfig.leftValueSmall) < index); // position area

      let hl10_last = hl10.filter(_ => _.index > range_start) // breakout area
      let lh10_last = lh10.filter(_ => _.index > range_start) // breakout area

      const middle = support[tradingRange]['price'] + (resist[tradingRange]['price'] - support[tradingRange]['price']) / 2
      const spread = percentageChange(support[tradingRange]?.["price"], resist[tradingRange]["price"]);
      var isBullishCand = data[index - 1]["c"] > data[index - 1]["o"]  // confirm exit



      const x = padding + index * candleWidth;
      const yHigh = padding + (1 - (cand.h - minPrice) / priceRange) * chartHeight;
      const yLow = padding + (1 - (cand.l - minPrice) / priceRange) * chartHeight;
      const yOpen = padding + (1 - (cand.o - minPrice) / priceRange) * chartHeight;
      const yClose = padding + (1 - (cand.c - minPrice) / priceRange) * chartHeight;


      var day = new Date(cand["t"]).getDay();
      // var isHolyday = hl.length < 2 || lh.length < 2 // day == 5 || day == 6; // SAT, SUN
      // var isHolyday = initalRangeStart + botConfig.leftValueSmall > index
      var isHolyday = 100 > index
      // if (isHolyday) Mark(ctx, { x1: x, y1: 30 }, "yellow", 4, 1)


      // find strong support and resist ****************************************************
      // var diffHeightView = Math.abs((priceCandle(resistBoxEnd, index)?.y1 - priceCandle(resistBoxStart, index)?.y2))
      var tolerance = .6
      var diffHeight = Math.abs(resistBoxEnd - resistBoxStart) * tolerance
      var lastHlZoneStart = hl.at(-1)?.c - (diffHeight / 2)
      var lastHlZoneEnd = hl.at(-1)?.c + (diffHeight / 2)
      var lastLhZoneStart = lh.at(-1)?.c - (diffHeight / 2)
      var lastLhZoneEnd = lh.at(-1)?.c + (diffHeight / 2)
      var hls_in_last_HL_zone = hl.slice(-2).filter(({ c }) => c > lastHlZoneStart && c < lastHlZoneEnd) // strong resist if length > 1
      var hls_in_last_LH_zone = lh.slice(-2).filter(({ c }) => c > lastLhZoneStart && c < lastLhZoneEnd) // strong support if length > 1
      // hls_in_last_HL_zone.length > 1 && Mark(ctx, { x1: priceCandle(hl.at(-1)?.c, index).x1, y1: priceCandle(hl.at(-1)?.c, index).y1 - (diffHeightView * tolerance) / 2 }, "#43fa9280", candleWidth, diffHeightView * tolerance)
      // hls_in_last_LH_zone.length > 1 && Mark(ctx, { x1: priceCandle(lh.at(-1)?.c, index).x1, y1: priceCandle(lh.at(-1)?.c, index).y1 - (diffHeightView * tolerance) / 2 }, "#fa654380", candleWidth, diffHeightView * tolerance)
      strong_support = hls_in_last_HL_zone.length > 1 ? lh.at(-1)?.c : strong_support
      strong_resist = hls_in_last_LH_zone.length > 1 ? hl.at(-1)?.c : strong_resist
      
      if(strong_resist){
        Mark(ctx, priceCandle(strong_resist, index), hls_in_last_HL_zone.length > 1 ? upColor : upColor, candleWidth, 2) // Last hl 
        Mark(ctx, priceCandle(strong_resist - (diffHeight / 2), index), upColor + 40, candleWidth, 1);
        Mark(ctx, priceCandle(strong_resist + (diffHeight / 2), index), upColor + 40, candleWidth, 1);
      }
      if(strong_resist){
        Mark(ctx, priceCandle(strong_support, index), hls_in_last_LH_zone.length > 1 ? downColor : downColor, candleWidth, 2) // Last lh 
        Mark(ctx, priceCandle(strong_support - (diffHeight / 2), index), upColor + 40, candleWidth, 1);
        Mark(ctx, priceCandle(strong_support + (diffHeight / 2), index), upColor + 40, candleWidth, 1);
      }
      // Mark(ctx, priceCandle(strong_resist, index), upColor + 90, candleWidth, 1);
      // Mark(ctx, priceCandle(supporstrong_resisttBoxStart, index), downColor + 90, candleWidth, 1);
      // Mark(ctx, priceCandle(strong_resist, index), downColor + 40, candleWidth, 1);


      // if (end) console.log(index, hls_in_last_LH_zone.length, strong_support);

      if (hls_in_last_HL_zone.length > 1) {
        // resist[tradingRange] = priceCandle(hl.at(-1)?.c, index)
        // update_support_resist(support[tradingRange]['price'], resist[tradingRange]['price'])
      }
      if (hls_in_last_LH_zone.length > 1) {
        // support[tradingRange] = priceCandle(lh.at(-1)?.c, index)
        // update_support_resist(support[tradingRange]['price'], resist[tradingRange]['price'])
      }
      // ******* end ********


      // CANDLE PATTERN
      // const prevCand = transformData(data[index - 1])
      // const currCand = transformData(data[index])

      // var bullishKicker = isBullishKicker(prevCand, currCand)
      // // if (isHammer(prevCand, currCand)) {
      // if (isBearishInvertedHammer(currCand)) {
      //   console.log(index, "HAMMER");
      //   Mark(ctx, priceCandle(middle, index), 'skyblue', candleWidth, 1);
      // }


      function ENTRY(type = "LONG", tag = null) {
        // if (index < 300) return
        if (isHolyday) return
        if (isOrderPlaced) return
        positionTmp["entryPrice"] = cand.o;
        positionTmp["x1"] = x;
        positionTmp["y1"] = yOpen;
        positionTmp["type"] = type;
        isOrderPlaced = true;
        Text(ctx, tag ?? type, x, yOpen, 'white');
        _emit(tag)
      }

      function EXIT(tag = null, exitPrice = cand.o) {
        if (!isOrderPlaced) return
        positionTmp["exitPrice"] = exitPrice // cand.o ;
        positionTmp["x2"] = x;
        positionTmp["y2"] = priceCandle(exitPrice)?.y2 // yOpen;
        positions.push(positionTmp);
        positionTmp = {};
        isOrderPlaced = false;
        position_span = 0;
        tag && Text(ctx, tag, x, yOpen - 120, 'red');
        _emit(tag)
        hl_temp_ = []
        lh_temp_ = []

        Status.remove("crossed_down")
        Status.remove("crossed_up")
      }


      function _emit(datalog) {
        if (!datalog) return
        if (index > logStartIndex) {
          setEvent({ index, log: datalog })
        }
      }


      // S & R
      if (!isHolyday && false) {
        Mark(ctx, priceCandle(resistBoxEnd, index), upColor + 40, candleWidth, 1);
        Mark(ctx, priceCandle(resistBoxStart, index), upColor + 90, candleWidth, 1);
        Mark(ctx, priceCandle(supportBoxStart, index), downColor + 90, candleWidth, 1);
        Mark(ctx, priceCandle(supportBoxEnd, index), downColor + 40, candleWidth, 1);
        Mark(ctx, priceCandle(middle, index), '#cccccc10', candleWidth, 1);
      }

      index % 5 == 0 && Text(ctx, index, x, 10, '#cccccc50');


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
        let change = percentageChange(cand.o, supportBoxEnd) // %
        let trailing = percentageChange(edgePrice, cand.o) // %
        let rangePos = percentageChange(edgePrice - lh.at(-1)?.c, edgePrice - cand.o) // %

        let range = 0
        let trailingExit = false

        if (hl_last.length > 0 && lh_last.length > 0) {

          let diff = hl_last.at(-1)?.c - lh_last.at(-1)?.c
          let supportResistArea = calculatePercentage(diff, botConfig.S_R_Area);
          var levelTopStart = hl_last.at(-1)?.c - supportResistArea / 2;
          var levelTopEnd = hl_last.at(-1)?.c + supportResistArea / 2;
          var levelBottomStart = lh_last.at(-1)?.c + supportResistArea / 2;
          var levelBottomEnd = lh_last.at(-1)?.c - supportResistArea / 2;

          Mark(ctx, priceCandle(levelTopStart, index), '#5e03fc90', candleWidth, 1);
          Mark(ctx, priceCandle(levelTopEnd, index), '#5e03fc90', candleWidth, 1);
          Mark(ctx, priceCandle(levelBottomStart, index), '#0367fc90', candleWidth, 1);
          Mark(ctx, priceCandle(levelBottomEnd, index), '#0367fc90', candleWidth, 1);

        }

        if (hl_last.length > 0 && lh_last.length > 0 && !Status.status('break_bearish_level_1')) {
          Text(ctx, 'Levels', x + 20, 120, 'yellow');
          Status.add('break_bearish_level_1')
        }

        if (Status.status('break_bearish_level_1') && cand.o > levelTopEnd) {
          EXIT()

          tradingRange += 1
          const maxLh = lh_last.slice(-2).reduce((min, item) => item.c < min ? item.c : min, Infinity);
          support[tradingRange] = priceCandle(lh_last.at(-1)?.c, index);
          // resist[tradingRange] = priceCandle(edgePrice, index);
          // support[tradingRange] = priceCandle(maxLh, index);
          resist[tradingRange] = priceCandle(hl_last.at(-1)?.c, index);
          update_support_resist(support[tradingRange]['price'], resist[tradingRange]['price'])
          breakout = 'await'
          range_start = index
          Status.remove('break_bearish_level_1')

          if (Math.abs(rangePos) > 70) {
            // ENTRY("SHORT")
          }

        }

        // Reverse
        if (!Status.status('break_bearish_level_1') && cand.o > supportBoxEnd) {
          EXIT()
          Text(ctx, 'R', x, 100, 'yellow');
          breakout = 'await'
          Status.remove('break_bearish_level_1')

          support[tradingRange] = priceCandle(edgePrice, index);
          update_support_resist(support[tradingRange]['price'], resist[tradingRange]['price'])
        }




      } // end bearish


      // if(end)console.log(reversalCandle);


      if (Status.status('fake_brk_down')) {
        Mark(ctx, priceCandle(middle, index), 'blue', candleWidth, 1);
      }
      if (Status.status('fake_brk_up')) {
        Mark(ctx, priceCandle(middle + 100, index), 'orange', candleWidth, 1);
      }



      if (breakout == "await" && !isHolyday) {

        // if (end) console.log({ isBullishCand });

        // LONG ENTRIES 
        if (cand.o < supportBoxStart && cand.o > supportBoxEnd) {
          // if (!Status.status('bearish')) ENTRY(undefined, 'LONG')
        } else if ((cand.o > resistBoxStart || data[index - 1].h > resistBoxStart) && positionTmp["type"] == 'LONG' && !isBullishCand) {
          EXIT('exit long')
          // ENTRY('SHORT')
        }


        // SHORT ENTRIES 
        if (cand.o > resistBoxStart && cand.o < resistBoxEnd) {
          // if (!Status.status('bullish')) ENTRY('SHORT')
        } else if ((cand.o < supportBoxStart || data[index - 1].l < supportBoxStart) && positionTmp["type"] == 'SHORT' && isBullishCand) {
          EXIT('exit short')
          // ENTRY(undefined, 'LONG')
        }





        // ////////////////////////////////////////// special entry exits  //////////////////////////////////////////
        if (positionTmp["type"] == 'SHORT') {
          // if (cand.o > lh.at(-1)?.c && cand.o < short_r_b_s_w_p_s) {
          //   EXIT('exit ' + positionTmp["type"])
          //   Text(ctx, "o > lh", x, priceCandle(edgePrice, index)['y1'], 'yellow');
          //   ENTRY()
          // }

          // if (cand.o < middle)status.push('crossed_down')
          // if (status.includes('crossed_down') && cand.o > middle && cand.o > lh.at(-1)?.c) EXIT('exit short')


          if (cand.o < strong_support && !Status.status('crossed_down')) Status.add('crossed_down')
          if (Status.status('crossed_down') && cand.o > strong_support) {
            EXIT('exit strong support cross up')
            image(ctx, 'return', x, yClose + 10)
            // ENTRY('SHORT', 'entry strong support cross up')
          }

          // if (lh_temp.length > 1 && lh_temp.at(-1)?.c > lh_temp.at(-2)?.c) {
          // EXIT('lh > lh-1')
          // image(ctx, 'bullish', x, resist[tradingRange]?.y1)
          // Status.add('bullish')
          // }

        }


        if (positionTmp["type"] == 'LONG') {
          // if (cand.o < hl.at(-1)?.c && cand.o < lh.at(-1)?.c && cand.o > r_b_s_w_p_s) {
          //   EXIT('exit long, ' + positionTmp["type"])
          //   Text(ctx, "o < hl", x, priceCandle(edgePrice, index)['y1'], 'yellow');
          //   ENTRY('SHORT')
          // }

          // if (cand.o > middle)  status.push('crossed_up')
          // if (status.includes('crossed_up') && cand.o < middle && cand.o < hl.at(-1)?.c) EXIT('exit long, ' + positionTmp["type"])

          if (cand.o > strong_resist && !Status.status('crossed_up')) Status.add('crossed_up')
          if (Status.status('crossed_up') && cand.o < strong_resist) {
            EXIT('exit strong resist cross down')
            image(ctx, 'return', x, yClose - 10)

            // ENTRY('SHORT', 'entry strong resist cross down')
          }

          // if (hl_temp.length > 1 && hl_temp.at(-1)?.c < hl_temp.at(-2)?.c) {
          //   EXIT('hl > hl-1')
          //   image(ctx, 'bearish', x, support[tradingRange]?.y1,)
          //   Status.add('bearish')
          // }
        }


        if (lh_last.length > 1 && lh_last.at(-1)?.c > lh_last.at(-2)?.c && cand.c > lh_last.at(-1)?.c && !Status.status('bullish')) {
          // EXIT('lh > lh-1')
          image(ctx, 'bullish', x, yClose + 10)
          Status.add('bullish')
        }

        if (hl_last.length > 1 && hl_last.at(-1)?.c < hl_last.at(-2)?.c && cand.c < hl_last.at(-1)?.c && !Status.status('bearish')) {
          // EXIT('hl > hl-1')
          image(ctx, 'bearish', x, yClose - 10)
          Status.add('bearish')
        }

        // retest



        if (hl_last.length > 2 && hl_last.slice(hl_last.length - 2).every(_ => (_.c < middle && _.c > supportBoxStart))) {
          Text(ctx, 'retest hl', x, 25);
          resist[tradingRange] = priceCandle(hl_last.at(-1)?.c, index);
          update_support_resist(support[tradingRange]['price'], resist[tradingRange]['price'])
          image(ctx, 'retest', x, yClose)
        }

        if (lh_last.length > 2 && lh_last.slice(lh_last.length - 2).every(_ => (_.c < middle && _.c > supportBoxStart))) {
          Text(ctx, 'retest lh', x, 25);
          support[tradingRange] = priceCandle(lh_last.at(-1)?.c, index);
          update_support_resist(support[tradingRange]['price'], resist[tradingRange]['price'])
          image(ctx, 'retest', x, yClose)

        }

        // lhs above middle


        if (hl_last.length > 2 && hl_last.slice(hl_last.length - 2).every(_ => (_.c < middle && _.c < resistBoxEnd))) {
          Text(ctx, 'retest hl', x, 25);
          resist[tradingRange] = priceCandle(hl_last.at(-1)?.c, index);
          update_support_resist(support[tradingRange]['price'], resist[tradingRange]['price'])
          image(ctx, 'retest', x, yClose)

        }

        if (lh_last.length > 2 && lh_last.slice(lh_last.length - 2).every(_ => (_.c > middle && _.c < resistBoxEnd))) {
          Text(ctx, 'retest hl', x, 25);
          support[tradingRange] = priceCandle(lh_last.at(-1)?.c, index);
          update_support_resist(support[tradingRange]['price'], resist[tradingRange]['price'])
          image(ctx, 'retest', x, yClose)
        }




      }





      if (breakout == "bullish") {
        edgePrice = cand.o > edgePrice ? cand.o : edgePrice
        // if (end) console.log(index);
        // status.push('freeze')
        let range = 0
        let change = percentageChange(resistBoxEnd, cand.o) // %
        let trailing = percentageChange(edgePrice, cand.o) // %
        let trailingExit = false
        let rangePos = percentageChange(edgePrice - lh.at(-1)?.c, edgePrice - cand.o)


        if (hl_last.length > 0 && lh_last.length > 0 && lh_last.at(-1)?.c > resistBoxEnd) {

          let diff = hl_last.at(-1)?.c - lh_last.at(-1)?.c
          let supportResistArea = calculatePercentage(diff, botConfig.S_R_Area);
          var levelTopStart = hl_last.at(-1)?.c - supportResistArea / 2;
          var levelTopEnd = hl_last.at(-1)?.c + supportResistArea / 2;
          var levelBottomStart = lh_last.at(-1)?.c + supportResistArea / 2;
          var levelBottomEnd = lh_last.at(-1)?.c - supportResistArea / 2;

          Mark(ctx, priceCandle(levelTopStart, index), '#5e03fc90', candleWidth, 1);
          Mark(ctx, priceCandle(levelTopEnd, index), '#5e03fc90', candleWidth, 1);
          Mark(ctx, priceCandle(levelBottomStart, index), '#0367fc90', candleWidth, 1);
          Mark(ctx, priceCandle(levelBottomEnd, index), '#0367fc90', candleWidth, 1);

        }

        if (hl_last.length > 0 && lh_last.length > 0 && !Status.status('break_bullish_level_1') && lh_last.at(-1)?.c > resistBoxEnd) {
          Text(ctx, 'Levels', x + 20, 120, 'yellow');
          Status.add('break_bullish_level_1')
        }

        if (Status.status('break_bullish_level_1') && cand.o < levelBottomEnd) {
          EXIT()

          tradingRange += 1
          const maxLh = lh_last.slice(-2).reduce((min, item) => item.c < min ? item.c : min, Infinity);
          resist[tradingRange] = priceCandle(hl_last.at(-1)?.c, index);
          // resist[tradingRange] = priceCandle(edgePrice, index);
          // support[tradingRange] = priceCandle(maxLh, index);
          support[tradingRange] = priceCandle(lh_last.at(-1)?.c, index);
          update_support_resist(support[tradingRange]['price'], resist[tradingRange]['price'])
          breakout = 'await'
          range_start = index
          Status.remove('break_bullish_level_1')

          if (Math.abs(rangePos) > 70) {
            // ENTRY("SHORT")
          }

        }

        // Reverse
        if (!Status.status('break_bullish_level_1') && cand.o < resistBoxEnd) {
          Text(ctx, 'R', x, 100, 'yellow');
          breakout = 'await'
          Status.remove('break_bullish_level_1')
          EXIT()

          resist[tradingRange] = priceCandle(edgePrice, index);
          update_support_resist(support[tradingRange]['price'], resist[tradingRange]['price'])
        }



        // if (hl10_last.at(-1)?.c > hl10_last.at(-2)?.c) {
        //   EXIT()
        // }


        // if (hl10_last.at(-1)?.c < hl10_last.at(-2)?.c) {
        //   EXIT()
        // }


      } // bullish end ******************


















      // if ((cand.o < supportBoxEnd && data[index - 1]?.o < supportBoxEnd && data[index - 1]?.c < supportBoxEnd) && breakout == 'await' && !isHolyday) {
        if ((strong_support && cand.o < strong_support) && breakout == 'await' && !isHolyday) {
        // if ((cand.o < supportBoxEnd) && breakout == 'await' && !isHolyday) {
        _emit('BEARISH breakout');
        breakout = "bearish"
        range_start = index
        // Text(ctx, 'bearish', x, priceCandle(lh_last.at(-1)?.c, index)['y1'], 'yellow');

        if (positionTmp["type"] != "SHORT") {
          // EXIT(undefined, supportBoxEnd)
          EXIT()
          ENTRY('SHORT', 'BRK-S')
          // if (hl_temp.length == 0 || hl_temp.at(-1)?.c < middle) ENTRY('SHORT', 'breakout S')
        }
      }



      // if ((cand.o > resistBoxEnd && data[index - 1]?.o > resistBoxEnd && data[index - 1]?.c > resistBoxEnd) && breakout == 'await' && !isHolyday) {
        if ((strong_resist && cand.o > strong_resist) && breakout == 'await' && !isHolyday) {
        // if ((cand.o > resistBoxEnd) && breakout == 'await' && !isHolyday) {
        _emit('BULLISH breakout');
        breakout = "bullish"
        range_start = index
        // Text(ctx, 'bullish', x, priceCandle(lh_last.at(-1)?.c, index)['y1'], 'yellow');

        if (positionTmp["type"] != "LONG") {
          // EXIT(undefined, resistBoxEnd)
          EXIT()
          ENTRY(undefined, 'BRK')
          // if (lh_temp.length == 0 || lh_temp.at(-1)?.c > middle) ENTRY(undefined, 'breakout L')
        }

      }




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

      if (hls[index]) {
        ctx.beginPath();
        ctx.arc(x, yClose, 6, 0, 2 * Math.PI);
        ctx.stroke();
        ctx.fillStyle = upColor;
        ctx.fill();
        hl_.push({ index, x, yClose, ...cand }); // 🔴
        hl_temp_.push({ index, x, yClose, ...cand });
      }

      if (lhs[index]) {
        ctx.beginPath();
        ctx.arc(x, yClose, 6, 0, 2 * Math.PI);
        ctx.stroke();
        ctx.fillStyle = downColor;
        ctx.fill();
        lh_.push({ index, x, yClose, ...cand }); // 🔴
        lh_temp_.push({ index, x, yClose, ...cand });
      }


      // HL/LH 10
      if (hls10[index]) {
        hl10_.push({ index, x, yClose, ...cand }); // 🔴

        ctx.beginPath();
        ctx.arc(x, yClose, 10, 0, 2 * Math.PI);
        ctx.stroke();
      }
      if (lhs10[index]) {
        lh10_.push({ index, x, yClose, ...cand }); // 🔴

        ctx.beginPath();
        ctx.arc(x, yClose, 10, 0, 2 * Math.PI);
        ctx.stroke();
      }


      // HH
      if (hhs[index]) {
        hh.push({ x, yClose }); // 
        ctx.beginPath();
        ctx.arc(x, yClose, 25, 0, 2 * Math.PI);
        ctx.stroke();
      }
      // LL
      if (lls[index]) {
        ll.push({ x, yClose }); // 
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

      // if (pl > 3) return

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