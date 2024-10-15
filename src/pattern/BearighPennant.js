import { drawLine, drawRect } from "./help";
import { nextLineEndpoint, calculatePercentage } from "./help";
var lineWidth = 30;
var data_boost = 5
const cval = (_) => window.innerHeight - _ * data_boost;

// data [0, 15, 20, 70, 45, 80, 65, 85, 75, 90, 85]

export default function BearighPennant(ctx, data_, minPivots = 6) {
    var data = [...data_].reverse();
    var len = data.length;
    var shapePivot = new Array(minPivots).fill(-1);
    if (len < shapePivot.length) return false;
    var goingup = data[0] > data[1]
  
    ////////// setp 1
    // Analyse shape 
    for (let i = 0; i < len; i++) {
      if(shapePivot.length > minPivots)break
        if ((i%2 == 0) && goingup ?  data[i] > data[i+1] : data[i] < data[i+1]) {
          // should below of prev
          shapePivot[i] = 0;
        }else if((i%2 == 1) && goingup ?  data[i] < data[i+1] : data[i] > data[i+1]){
          // should above of prev
          shapePivot[i] = 0;
        }else{
            // console.log("break on", i);
          break
        }
    }
    if(shapePivot.length < minPivots)return
  
    var gotShape_1 = !shapePivot.some((_) => _ != 0)
    // console.log("gotShape_1", shapePivot);
    if(!gotShape_1)return false
  
    ////////// setp 2
  
  
  
    for (let i = 0; i < shapePivot.length; i++) {
      if(i<2)continue;
      if(i % 2 == 0){
        if(data[i] > data[i+2]){
            // console.log("OK BOTTOM");
            shapePivot[i] = 1;
          }
          else{
            shapePivot[i] = -1;
          }
        }
        drawLine(ctx, ((len-i)-2)*lineWidth, cval(data[i]), ((len-i)+2)*lineWidth, cval(data[i]), "red", 1);
        
      if(i % 2 == 1){
        if(data[i] < data[i+2]){
            // console.log("OK TOP");
            shapePivot[i] = 1;
          }else{
            shapePivot[i] = -1;
          }
          drawLine(ctx, ((len-i)-2)*lineWidth, cval(data[i]), ((len-i)+2)*lineWidth, cval(data[i]), "green", 1);
      }
    }
  
  
    var gotShape_2 = !shapePivot.slice(2).some((_) => _ == -1)
    console.log("gotShape_2 =====>", shapePivot.slice(2));
    if(!gotShape_2)return false

     // N E C K  L I N E

     var odd = shapePivot.length % 2 == 0 ? 1 : 2 // 
    // support 
      var supportX1 = (len-shapePivot.length+(odd==2 ? 1: 2))*lineWidth
      var supportY1 = cval(data[shapePivot.length-(odd==2 ? 1: 2)])
      var supportX2 = (len-2)*lineWidth
      var supportY2 = cval(data[2])
    // resist
      var resistX1 = (len-shapePivot.length+odd)*lineWidth
      var resistY1 = cval(data[shapePivot.length-odd]) 
      var resistX2 = (len-1)*lineWidth
      var resistY2 = cval(data[1])

      // Ratio compare
      var rangeHeightStart = supportY1 - resistY1
      var resistHeight = supportY1-resistY2  
      var supportHeight = supportY1-supportY2
      var resistPercent = (resistHeight*100/rangeHeightStart).toFixed(0)
      var supportPercent = (supportHeight*100/rangeHeightStart).toFixed(0)
      
      // draw
      ctx.font = "20px";
      ctx.fillText(resistPercent+"%", resistX2,resistY2);
      ctx.fillText(supportPercent+"%", supportX2,supportY2);
 
      if(resistPercent < 60 && supportPercent > 20)return // shold match the ration

      
      drawLine(ctx, supportX1,supportY1,supportX2,supportY2);
      // support infinte
      var supportNext = nextLineEndpoint(supportX1,supportY1,supportX2,supportY2)
      drawLine(ctx, supportX2,supportY2, supportNext.x, supportNext.y, undefined, 1);
      
      drawLine(ctx, resistX1,resistY1,resistX2,resistY2, cval(data[2]));
      // resist infinte
      var resistNext = nextLineEndpoint(resistX1,resistY1,resistX2,resistY2)
      drawLine(ctx, resistX2,resistY2, resistNext.x, resistNext.y, undefined, 1);
  
    // result
    return gotShape_2;
  }