function calculatePercentage(value, percentage) {
  // if (isNaN(value) || isNaN(percentage)) {
  //   throw new Error("Both value and percentage must be numbers.");
  // }

  // if (percentage < 0 || percentage > 100) {
  //   throw new Error("Percentage must be between 0 and 100.");
  // }

  return (value * percentage) / 100;
}

function percentageChange(num1, num2) {
  const diff = num2 - num1
  return diff * 100 / num1
}


function calculateFee(orderValue, leverage, feeRate) {
  // Convert fee rate to a decimal
  const feeRateDecimal = feeRate / 100;

  // Calculate the fee using the formula
  const fee = (orderValue * leverage * feeRateDecimal);

  return fee;
}

const log = (..._) => console.log(..._)




function calculateRSI(prices, period = 14) {
  if (prices.length < period) {
    throw new Error("Not enough prices to calculate RSI.");
  }

  const changes = [];
  for (let i = 1; i < prices.length; i++) {
    changes.push(prices[i] - prices[i - 1]);
  }

  const gains = [];
  const losses = [];
  for (let i = 0; i < changes.length; i++) {
    if (changes[i] > 0) {
      gains.push(changes[i]);
      losses.push(0);
    } else {
      gains.push(0);
      losses.push(-changes[i]);
    }
  }

  let averageGain = gains.slice(0, period).reduce((acc, val) => acc + val, 0) / period;
  let averageLoss = losses.slice(0, period).reduce((acc, val) => acc + val, 0) / period;

  const rsArray = [];
  rsArray.push(averageGain / averageLoss);

  for (let i = period; i < prices.length; i++) {
    averageGain = (averageGain * (period - 1) + gains[i]) / period;
    averageLoss = (averageLoss * (period - 1) + losses[i]) / period;
    rsArray.push(averageGain / averageLoss);
  }

  const rsiArray = rsArray.map(rs => 100 - (100 / (1 + rs)));

  return rsiArray;
}



const calculateRSIMA = (rsi, period = 14) => {
  const ma = [];
  for (let i = 0; i < rsi.length; i++) {
    if (i < period - 1) {
      ma.push(null);
    } else {
      const avg = rsi.slice(i - period + 1, i + 1).reduce((acc, val) => acc + val, 0) / period;
      ma.push(avg);
    }
  }
  return ma;
};

function calculateSMA_(prices, period = 14) {
  if (prices.length < period) {
    throw new Error("Not enough prices to calculate SMA.");
  }

  // Slice the array from the back
  const slicedPrices = prices.slice(-period);

  const sum = slicedPrices.reduce((acc, val) => acc + val, 0);
  const sma = sum / period;

  return sma;
}


// https://www.binance.com/en-IN/futures/trading-rules/perpetual/leverage-margin



// // Example usage:
// let entryPrice = 10000; // Price at which the asset was bought
// let positionSize = 5; // Number of units of the asset (e.g., 5 BTC)
// let positionType = "long"; // Type of position: "long" or "short"

// // Calculate Notional Position Value
// let notionalPositionValue = calculateNotionalPositionValue(entryPrice, positionSize);
// console.log("Notional Position Value:", notionalPositionValue);

// // Determine the appropriate tier
// let tier = getTier(notionalPositionValue);
// console.log("Tier:", tier);

// // Calculate Initial Margin
// let initialMargin = calculateInitialMargin(entryPrice, positionSize, tier.maxLeverage);
// console.log("Initial Margin:", initialMargin);

// // Calculate Maintenance Margin
// let maintenanceMargin = calculateMaintenanceMargin(notionalPositionValue, tier.maintenanceMarginRate, tier.maintenanceAmount);
// console.log("Maintenance Margin:", maintenanceMargin);

// // Calculate Liquidation Price
// let liquidationPrice = calculateLiquidationPrice(entryPrice, tier.maxLeverage, tier.maintenanceMarginRate, tier.maintenanceAmount, positionSize, positionType);
// console.log("Liquidation Price:", liquidationPrice);



function transformData(data) {
  const date = new Date(data.t).toISOString().split('T')[0];
  return {
    security: 'ORCL',
    date: date,
    open: data.o,
    high: data.h,
    low: data.l,
    close: data.c
  };
}



export { calculatePercentage, percentageChange, calculateFee, log, calculateRSI, calculateRSIMA, transformData};


