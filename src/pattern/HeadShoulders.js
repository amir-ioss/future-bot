import { drawLine, drawRect } from "./help";
import { nextLineEndpoint, calculatePercentage } from "./help";

var lineWidth = 30;
var data_boost = 5
const cval = (_) => window.innerHeight - _ * data_boost;

export default function HeadShoulders(ctx, data_, pivotBalance = 30) {
    var data = [...data_].reverse();
    var len = data.length;
    var shapePivot = [-1, -1, -1, -1, -1, -1,-1];
    if (len < shapePivot.length) return false;
    var patternData = data.slice(1, shapePivot.length);
  
    ////////// setp 1
    // Analyse shape 
    for (let i = 0; i < shapePivot.length; i++) {
        if (i%2 == 0 && data[i] < data[i+1]) {
          // should below of prev
          shapePivot[i] = 0;
        }else if(i%2 == 1 && data[i] > data[i+1]){
          // should above of prev
          shapePivot[i] = 0;
        }
    }
  
    var gotShape_1 = !shapePivot.some((_) => _ != 0)
    // console.log("gotShape_1", shapePivot);
    if(!gotShape_1)return false
  
    ////////// setp 2
  
     // N E C K  L I N E
      // neckline top
      var necklineTop = Math.max(...patternData)
      var necklineBottom = Math.min(...patternData)
      var offset =  len - shapePivot.length
      var avgNeckHeight = calculatePercentage(necklineTop - necklineBottom, pivotBalance/2)
      var cNeckHeight = avgNeckHeight*data_boost
  
    for (let i = 0; i < shapePivot.length; i++) {
      // neck top edge
      var topNeckTop = cval(necklineTop)-cNeckHeight
      var topNeckBotton = cval(necklineTop)+cNeckHeight
      // neck bottom edge
      var botNeckTop = cval(necklineBottom)-cNeckHeight
      var botNeckBotton = cval(necklineBottom)+cNeckHeight
  
      // i == 0 && console.log(i, data[i], cval(data[i]) , topNeckTop ,'&&', cval(data[i]) , topNeckBotton);
      // if (i%2 == 0 && cval(data[i]) > botNeckTop && cval(data[i]) < botNeckBotton) {
      //   // should below of prev
      //   shapePivot[i] = 1;
      // }else if(i%2 == 1 && cval(data[i]) > topNeckTop && cval(data[i]) < topNeckBotton){
      //   // should above of prev
      //   shapePivot[i] = 1;
      // }
      if(i == 2 || i == 4){
        drawLine(ctx, (len-i)*lineWidth, cval(data[i]), ((len-i)-1)*lineWidth, cval(data[i]), i % 2 == 0 ? "green" : "blue", 1);
        drawRect(ctx, (len - i) * lineWidth, cval(data[i]), -lineWidth * 2, 30, i % 2 == 0 ? "green" : "blue", 1);
      }

      if(i%2 == 1 && data[i] > data[i+2] && data[i] > data[i-2] && i == 3){
        // console.log(i);
        shapePivot[i] = 1

      }else{
        shapePivot[i] = 1
      }
    }
  
  
    var gotShape_2 = !shapePivot.some((_) => _ == 0)
    console.log("gotShape_2 =====>", shapePivot);
    if(!gotShape_2)return false
     
      // drawLine(ctx, offset*lineWidth, cval(necklineTop), len*lineWidth, cval(necklineTop), 'black', 1);
      // drawRect(ctx, offset*lineWidth, cval(necklineTop)-(cNeckHeight),  (len*lineWidth-offset*lineWidth), cNeckHeight*2,  "green", 1);
      // // neckline bottom
      // drawLine(ctx, offset*lineWidth, cval(necklineBottom), len*lineWidth, cval(necklineBottom), 'black', 1);
      // drawRect(ctx, offset*lineWidth, cval(necklineBottom)-(cNeckHeight),  (len*lineWidth-offset*lineWidth), cNeckHeight*2,  "green", 1);
  
    // result
    return gotShape_2;
  }