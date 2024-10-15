import React, { useState, useEffect } from 'react';
import dates from '../data/data'

const JsonLoader = ({ setJsonData = () => null }) => {
  const [selectedDate, setSelectedDate] = useState('2023-02-15'); // 2022-01-31
  const [index, setIndex] = useState(0);

  useEffect(() => {
    // Assuming your JSON files are in the data folder
    const fetchData = async () => {
      try {
        const response = await import(`../data/ohlcv/${selectedDate}.json`);
        setJsonData(response.default);
      } catch (error) {
        console.error('Error loading JSON data:', error);
        setJsonData(null);
      }
    };

    fetchData();

    document.addEventListener('keydown', keyPress);
    return () => {
      document.removeEventListener('keydown', keyPress);
    }

  }, [selectedDate]);


  const keyPress = (e) => {
    if (e.which == 39) {
      setSelectedDate(dates[index + 1])
      setIndex(index + 1)
    }
    if (e.which == 37) {
      setSelectedDate(dates[index - 1])
      setIndex(index - 1)
    }
  }


  return (<>
    <select
      id="dateSelect"
      value={selectedDate}
      onChange={(event) => {
        setIndex(dates.indexOf(event.target.value))
        setSelectedDate(event.target.value)
      }}
    >
      {dates.map((date, key) => {
        return <option value={date} key={key}>{date}</option>
      })}
    </select>
  </>
  );
};

export default JsonLoader;
