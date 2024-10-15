import { drawLine, drawRect } from "./help";
import { nextLineEndpoint, calculatePercentage } from "./help";
var lineWidth = 30;
var data_boost = 5
const cval = (_) => window.innerHeight - _ * data_boost;

// data [0, 15,70, 30, 69, 29, 71, 32, 75 ]


export default function BullishRectangle(ctx, data_, pivotBalance = 30, minPivots = 6) {
    var data = [...data_].reverse();
    var len = data.length;
    var shapePivot = new Array(minPivots).fill(-1);
    if (len < shapePivot.length) return false;
    var goingup = data[0] > data[1]

  
    ////////// setp 1
    // Analyse shape 
    for (let i = 0; i < shapePivot.length; i++) {
        if (i%2 == 0 && (goingup ? data[i] > data[i+1] : data[i] < data[i+1])){
          shapePivot[i] = 0;
        }else if(i%2 == 1 && (goingup ? data[i] < data[i+1] : data[i] > data[i+1])){
          shapePivot[i] = 0;
        }else{
          break
        }
    }
    if(shapePivot.length < minPivots)return
  
    var gotShape_1 = !shapePivot.some((_) => _ != 0)
    // console.log("gotShape_1", shapePivot);
    if(!gotShape_1)return false
  
    ////////// setp 2

    // draw neck
    var patternData = data.slice(0, shapePivot.length);

    var necklineTop = Math.max(...patternData)
    var necklineBottom = Math.min(...patternData)
    var offset =  len - shapePivot.length
    var avgNeckHeight = calculatePercentage(necklineTop - necklineBottom, pivotBalance/2)
    var topNeckHigh = necklineTop+avgNeckHeight
    var topNeckLow = necklineTop-avgNeckHeight
    var botNeckHigh = necklineBottom-avgNeckHeight
    var botNeckLow = necklineBottom+avgNeckHeight

  
  
    for (let i = 0; i < shapePivot.length; i++) {
      if(i % 2 == 0){
        if(goingup ? data[i] < topNeckHigh && data[i] > topNeckLow :  data[i] < botNeckHigh && data[i] > botNeckLow){
            shapePivot[i] = 1;
        }else{
            shapePivot[i] = -1;
        }
        // drawLine(ctx, ((len-i))*lineWidth, cval(data[i]), ((len-i)-2)*lineWidth, cval(data[i]), "black", 1);
      }

      if(i % 2 == 1){
        if(goingup ? data[i] > botNeckHigh && data[i] < botNeckLow :  data[i] > topNeckHigh && data[i] < topNeckLow){
            shapePivot[i] = 1;
        }else{
            shapePivot[i] = -1;
        }
        // drawLine(ctx, ((len-i))*lineWidth, cval(data[i]), ((len-i)-2)*lineWidth, cval(data[i]), "black", 1);
      }
    }
  
  
    var gotShape_2 = !shapePivot.slice(2).some((_) => _ == -1)
    // console.log("gotShape_2 =====>", shapePivot);
    if(!gotShape_2)return false

    // N E C K  L I N E

    drawLine(ctx, (offset)*lineWidth, cval(topNeckHigh), len*lineWidth, cval(topNeckHigh), "green", 1);
    drawLine(ctx, (offset)*lineWidth, cval(topNeckLow), len*lineWidth, cval(topNeckLow), "green", 1);

    drawLine(ctx, (offset)*lineWidth, cval(botNeckHigh), len*lineWidth, cval(botNeckHigh), "red", 1);
    drawLine(ctx, (offset)*lineWidth, cval(botNeckLow), len*lineWidth, cval(botNeckLow), "red", 1);

  
    // result
    return gotShape_2;
  }