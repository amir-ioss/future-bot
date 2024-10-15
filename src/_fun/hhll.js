// Sample OHLCV data

const ohlcvData = [
  { o: 100, h: 110, l: 95, c: 105, v: 1000 },
  { o: 105, h: 120, l: 100, c: 115, v: 1500 },
  { o: 115, h: 130, l: 110, c: 125, v: 2000 },
  { o: 120, h: 140, l: 115, c: 135, v: 1800 },
  // Add more data points as needed
];

// Function to find higher highs and lower lows
function findHigherHighsAndLowerLows(data) {
  const result = [];
  let currentHigh = data[0].h;
  let currentLow = data[0].l;

  for (let i = 1; i < data.length - 1; i++) {
    const currentData = data[i];
    const nextData = data[i + 1];

    if (currentData.h > currentHigh && currentData.h > nextData.h) {
      result.push({ type: "higherHigh", data: currentData });
      currentHigh = currentData.h;
    }

    if (currentData.l < currentLow && currentData.l < nextData.l) {
      result.push({ type: "lowerLow", data: currentData });
      currentLow = currentData.l;
    }
  }
  return result;
}



function pivothigh(high, left, right) {
  const pivots = high.map((value, index) => {
    if (index < left || index >= high.length - right) return NaN;

    const maxInRange = Math.max(...high.slice(index - left, index + right + 1));
    return value === maxInRange ? value : NaN;
  });

  return pivots;
}

function pivotlow(low, left, right) {
  const pivots = low.map((value, index) => {
    if (index < left || index >= low.length - right) return NaN;

    const minInRange = Math.min(...low.slice(index - left, index + right + 1));
    return value === minInRange ? value : NaN;
  });

  return pivots;
}


export {findHigherHighsAndLowerLows, pivothigh, pivotlow}
// Call the function with the OHLCV data
// const higherHighsAndLowerLows = findHigherHighsAndLowerLows(ohlcvData_);
// console.log(higherHighsAndLowerLows);
