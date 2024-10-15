import React, { useEffect, useState } from 'react'
import { calculatePercentage, percentageChange } from './_fun/helpers';
import { getMonthName } from './_fun/draw';


function calculateProfitLoss(position) {
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
  // const fee_entry = calculateFee(INVEST, LEVERAGE, FEE);
  // const fee_exit = calculateFee(exit_size, LEVERAGE, FEE);

  let pl =
    l_exit_size - l_entry_size - (amount_entry_fee + amount_exit_fee);

  if (position["type"] == "SHORT") {
    pl = l_entry_size - l_exit_size - (amount_entry_fee + amount_exit_fee);
  }

  return pl

}


function Paper() {
  const [data, setData] = useState([]);


  useEffect(() => {
    const paper_data = async () => {
      try {
        const response = await fetch('http://127.0.0.1:8000/test');
        const data = await response.json();
        // console.log({data});
        setData(data);
      } catch (error) {
        console.error('Error fetching the ping response:', error);
      }
    };
    paper_data();
  }, []);

  if (!data) return <p>Analysing...</p>

  var total = 0

  return (
    <div className='paper'>
      {data.map((chart, idx) => {
        let pnl = chart.positions.reduce((total, pos) => {
          return total + calculateProfitLoss(pos);
        }, 0);

        total += pnl


        return <div key={idx} className={`chart-card ${pnl > 0 ? 'bg-[#00ff8420]' : 'bg-[#ff000010]'}`}  >
          <p className="opacity-40"><span className="mr-2">{chart.date + 1}</span>{getMonthName(chart.date)}</p>
          <p className="text-xl " style={{ color: pnl > 0 ? 'green' : 'red' }}>{pnl.toFixed(2)}</p>
          <div className='pos-card'>
            {chart.positions.map((pos, id) => {
              var pl = calculateProfitLoss(pos)
              return <span key={id} style={{ color: pl > 0 ? 'green' : '#700f0f' }}>{pl.toFixed(2)}</span>
            })}
          </div>
        </div>
      })}

      <h1 style={{ color: total > 0 ? 'green' : 'red' }}>{total.toFixed(2)}<span className='text-white opacity-30'> {(total * 4).toFixed(2)} / 100</span></h1>

    </div>
  )
}

export default Paper