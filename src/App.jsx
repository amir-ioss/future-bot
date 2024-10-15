import React, { useEffect, useRef, useState } from "react";
// import CustomCandlestickChart from "./ChartT.jsx";
import CustomCandlestickChart from "./Chart.jsx";
// import CustomCandlestickChart from "./ChartTBR.jsx";
// import CustomCandlestickChart from "./ChartRSI.jsx";
import Paper from "./Paper.jsx";
import JsonLoader from './_fun/JsonLoader.jsx'
import botConfig from "./botConfig";
import {
  findHigherHighsAndLowerLows,
  pivothigh,
  pivotlow,
} from "./_fun/hhll.js";
import { useStore } from "./store.jsx";

const data_offet = 0;
const data_len = 1000;
const speed = 1
const playSpeed = 4



function ChartView() {
  const [fullData, setFullData] = useState([]);
  const [data, setData] = useState([]);
  const [bot, setBot] = useState();
  const [viewConfig, setViewConfig] = useState({
    data_offet,
    data_len,
    speed,
    play: false
  });

  const { events, activeCand, setActiveCand, setEvent, setEventClear } = useStore()


  // const modifyData = ohlcv_data => ohlcv_data.slice(viewConfig.data_offet, viewConfig.data_len).map((_, k) => ({ t: _[0], o: _[1], h: _[2], l: _[3], c: _[4], v: _[5] }));
  const modifyData = ohlcv_data => ohlcv_data.map((_, k) => ({ t: _[0], o: _[1], h: _[2], l: _[3], c: _[4], v: _[5] }));


  useEffect(() => {
    //   setData(modifyData(fullData));
    setData(prevData => modifyData(fullData));
  }, [viewConfig.data_len, viewConfig.data_offet]);



  useEffect(() => {
    const bot_ai = async () => {
      try {
        const response = await fetch('http://127.0.0.1:8000/bot');
        const data = await response.json();
        // console.log({data});
        setBot(data);
        setData(modifyData(data.candles));
      } catch (error) {
        console.error('Error fetching the ping response:', error);
      }
    };
    bot_ai();
  }, []);



  useEffect(() => {
    let animationFrameId = null;
    let lastUpdate = Date.now();

    const updateData = () => {
      const now = Date.now();
      if (now - lastUpdate >= playSpeed) {
        lastUpdate = now;
        setViewConfig(prev => ({ ...prev, data_len: parseInt(prev.data_len) + prev.speed }));
        setData(prevData => modifyData(fullData));
      }
      animationFrameId = requestAnimationFrame(updateData);
    };

    if (viewConfig.play) {
      updateData();
    } else {
      cancelAnimationFrame(animationFrameId);
    }

    return () => cancelAnimationFrame(animationFrameId);
  }, [viewConfig.play, fullData]);




  // HORIZONTAL SCROLL
  const scrollableRef = useRef(null);
  useEffect(() => {
    const handleScroll = (event) => {
      event.preventDefault();
      const container = scrollableRef.current;
      if (container) {
        const speed = event.shiftKey ? 0.1 : 3;
        container.scrollLeft += event.deltaY * speed;
      }
    };

    const container = scrollableRef.current;
    if (container) {
      container.addEventListener('wheel', handleScroll, { passive: false });
    }

    // Clean up the event listener when the component unmounts
    return () => {
      if (container) {
        container.removeEventListener('wheel', handleScroll);
      }
    };
  }, []);

  // console.log("-", findHigherHighsAndLowerLows(data));

  var close = data.map((_, k) => _.c);

  const hhs = pivothigh(close, botConfig.leftValue, botConfig.rightValue);
  const lls = pivotlow(close, botConfig.leftValue, botConfig.rightValue);
  // console.log("Pivot Highs:", hhs);
  // console.log("Pivot Lows:", lls);

  const hls = pivothigh(
    close,
    botConfig.leftValueSmall,
    botConfig.rightValueSmall
  );

  const lhs = pivotlow(
    close,
    botConfig.leftValueSmall,
    botConfig.rightValueSmall
  );

  const hls10 = pivothigh(
    close,
    10,
    10
  );

  const lhs10 = pivotlow(
    close,
    10,
    10
  );


  // console.log(Math.max(...hls.filter(_ =>_).slice(0,3)));
  var initialResistAr = hls.filter((_) => _).slice(0, 1);
  var initalRangeStartR = hls.indexOf(Math.max(...initialResistAr));


  var initialSupportAr = lhs.filter((_) => _).slice(0, 1);
  var initalRangeStartS = lhs.indexOf(Math.min(...initialSupportAr));


  return (
    <div>
      <div className="dashboard">
        <JsonLoader setJsonData={json => {
          setData(modifyData(json))
          setFullData(json)
        }} />
        <input
          value={viewConfig.data_offet}
          placeholder="*"
          onChange={(e) =>
            setViewConfig({ ...viewConfig, data_offet: e.target.value })
          }
        />
        <input
          value={viewConfig.data_len}
          placeholder="*"
          onChange={(e) =>
            setViewConfig({
              ...viewConfig,
              data_len: e.target.value == "" ? 1000 : e.target.value,
            })
          }
        />
        <button
          onClick={() => {
            setViewConfig({
              ...viewConfig,
              data_len: parseInt(viewConfig.data_len) - viewConfig.speed,
            });
          }}
          style={{ paddingLeft: 40, paddingRight: 40 }}
        >
          -
        </button>
        <button
          onClick={() => {
            setEventClear()
            setViewConfig({
              ...viewConfig,
              data_len: parseInt(viewConfig.data_len) + viewConfig.speed,
            });
          }}
          style={{ paddingLeft: 40, paddingRight: 40 }}
        >
          +
        </button>


        {[1, 5, 10, 20, 100, 500].map((spd, idx) => {
          return <button key={'speed_' + idx}
            onClick={() => setViewConfig({ ...viewConfig, speed: spd })}
            style={{ paddingLeft: 10, paddingRight: 10, color: viewConfig.speed == spd ? 'black' : '#aaa' }}
          >{spd}</button>
        })}
        <button
          onClick={() => {
            setEventClear()
            setViewConfig({
              ...viewConfig,
              data_len,
            });
          }}
          style={{ paddingLeft: 10, paddingRight: 10 }}
        >
          reset
        </button>

        <button
          onClick={() => {
            setViewConfig(prev => ({ ...prev, play: !prev.play }));
          }}
          style={{ paddingLeft: 10, paddingRight: 10 }}
        >
          {viewConfig.play ? 'pause' : 'play'}
        </button>

      </div>

      {/* <div className="logs">
        {events.map((evt, id) => {
          return <div key={'evnt_' + id}>
            <p className="logs_txt">{evt.log} -{evt.index + 1}</p>
          </div>
        })}
      </div> */}

      {activeCand && <div style={{
        position: 'absolute',
        backgroundColor: '#fff',
        // left: activeCand.pos.x * 10,
        top: activeCand.pos.y,
        right: 0,
        padding: 2
      }}>
        <p className="bold">{activeCand.index}</p>
        <p className="bold">{formatRailwayTime(activeCand.cand.t)}</p>
        <p className="text-sm">{activeCand.cand.o}</p>
        <p className="text-sm">{activeCand.cand.h}</p>
        <p className="text-sm">{activeCand.cand.l}</p>
        <p className="text-sm">{activeCand.cand.c}</p>
      </div>}



      <div className="horizontal-scroll-container" ref={scrollableRef}>
        {bot && <CustomCandlestickChart
          data={data}
          bot={bot}
          hhs={hhs}
          lls={lls}
          hls={hls}
          lhs={lhs}
          initalRangeStart={
            initalRangeStartR > initalRangeStartS
              ? initalRangeStartR
              : initalRangeStartS
          }
          initialResist={Math.max(...initialResistAr)}
          initialSupport={Math.min(...initialSupportAr)}
          closes={close}
          hls10={hls10}
          lhs10={lhs10}
        />}


      </div>
    </div>
  );
}





export default function App() {
  // State to track the current view
  const [view, setView] = useState('chart');

  // Function to switch views
  const renderView = () => {
    switch (view) {
      case 'chart':
        return <ChartView />;
      case 'paper':
        return <Paper />;
      default:
        return <ChartView />;
    }
  };

  return (
    <div className="main" >
      <nav>
        <button onClick={() => setView('home')} className="mr-4">Home</button>
        <button onClick={() => setView('paper')} className="mr-4">Paper</button>
      </nav>
      {renderView()}
    </div>
  );
}




function formatRailwayTime(timestamp) {
  const date = new Date(timestamp);
  const hours = date.getHours();
  const minutes = date.getMinutes();
  const formattedHours = hours < 10 ? '0' + hours : hours;
  const formattedMinutes = minutes < 10 ? '0' + minutes : minutes;
  return `${formattedHours}:${formattedMinutes}`;
}
