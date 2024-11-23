from flask import Flask, send_file, render_template_string

app = Flask(__name__)


# look

# Paths to your log files
# scalp_log = '/home/ioss/Documents/Learn/future-bot/bot/scalp/log.txt'
# scalp_terminal = '/home/ioss/Documents/Learn/future-bot/bot/log.log'

scalp_log = '/home/ec2-user/bot/scalp/log.txt'
scalp_terminal = '/home/ec2-user/bot/scalp/nohup.log'


swing_log = '/home/ec2-user/swing/log.txt'
swing_terminal = '/home/ec2-user/swing/nohup.log'

default_log_file = scalp_log


@app.route('/')
def index():
    # HTML with two buttons to load different logs
    html_content = '''<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Bot Log Viewer</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script
      src="https://code.jquery.com/jquery-3.7.1.min.js"
      integrity="sha256-/JqT3SQfawRcv/BIHPThkBvs0OEvtFFmqPF/lYI/Cxo="
      crossorigin="anonymous"
    ></script>
  </head>
  <body class="bg-black text-white text-sm">
    <div class="flex items-center gap-x-2">
      <h2 class="text-2xl">Log Viewer</h2>

      <button class="border border-green-400 p-2" onclick="loadLog()">
        Cards
      </button>

      <button
        class="border border-green-400 p-2"
        onclick="loadLog(`scalp_log`)"
      >
        Scalp Log
      </button>
      <button
        class="border border-green-400 p-2"
        onclick="loadLog(`scalp_terminal`)"
      >
        Scalp Terminal
      </button>

      <button
        class="border border-green-400 p-2"
        onclick="loadLog(`swing_log`)"
      >
        Swing Log
      </button>
      <button
        class="border border-green-400 p-2"
        onclick="loadLog(`swing_terminal`)"
      >
        Swing Terminal
      </button>

      <div
        class="h-2 flex flex-1 bg-gray-600 ml-8 rounded-full overflow-hidden"
      >
        <div id="wins_bar" class="h-2 bg-green-600"></div>
        <div id="los_bar" class="h-2 bg-red-600"></div>
      </div>

      <p id="wins" class="text-green-400">_</p>
      <p id="los" class="text-red-400 mr-8">_</p>
    </div>

    <!-- LONG -->
    <div
      id="active_long"
      class="hidden mb-2 relative text-slate-400 items-center bg-gradient-to-t to-transparent p-3 rounded-lg border-x border-b-red-600 border-slate-600 min-w-2xl h-64"
    >
      <h1 class="text-2xl">
        <span class="bg-green-600 text-xl p-1 mr-2 text-white">LONG</span
        ><span id="symbol">___/USDT</span>
      </h1>

      <div class="flex items-center">
        <p class="text-4xl my-2" id="cur_change">0%</p>
        <div class="ml-4">
          <p>↑ <span id="high_change">0%</span></p>
          <p>↓ <span id="low_change">0%</span></p>
        </div>
      </div>

      <p class="text-4xl my-2" id="cur_price">0.00</p>

      <div
        id="entry_line"
        class="absolute w-full border-b border-dashed border-slate-400 left-0"
      >
        <p class="h-fit flex justify-end text-xs mr-4">0.00</p>
      </div>
      <div
        id="cur_price_line"
        class="absolute w-full h-[1px] bg-orange-400 left-0"
      >
        <p class="h-fit flex justify-end text-xs mr-4">0.00</p>
      </div>

      <div
        id="style_sl"
        class="absolute left-0 bg-gradient-to-t from-red-500/30 bottom-0 h-4 w-full"
      >
        <p class="h-fit flex justify-end items-end text-xs mr-4 h-full">
          0.00 sl
        </p>
      </div>
      <div
        id="style_tp"
        class="absolute left-0 top-0 bg-gradient-to-b from-green-500/30 bottom-0 h-4 w-full"
      ></div>
    </div>

    <!-- SHORT -->
    <div
      id="active_short"
      class="hidden relative items-center bg-gradient-to-t to-transparent p-3 rounded-lg border-x border-t border-t-red-600 border-slate-600 min-w-2xl h-64"
    >
      <h1 class="text-2xl">
        <span class="bg-red-600 text-xl p-1 mr-2 text-white">SHORT</span
        ><span id="symbol_s">___/USDT</span>
      </h1>
      <div class="flex items-center">
        <p class="text-4xl my-2" id="cur_change_s">0%</p>
        <div class="ml-4">
          <p>↑ <span id="high_change_s">0%</span></p>
          <p>↓ <span id="low_change_s">0%</span></p>
        </div>
      </div>
      <p class="text-4xl text-slate-400 my-2" id="cur_price_s">0.00</p>

      <div
        id="entry_line_s"
        class="absolute w-full border-b border-dashed border-slate-400 left-0"
      >
        <p class="flex justify-end text-xs text-slate-400 mr-4 h-0">0.00</p>
      </div>
      <div
        id="cur_price_line_s"
        class="absolute w-full h-[1px] bg-orange-400 left-0"
      >
        <p class="h-fit flex justify-end text-xs text-slate-400 mr-4">0.00</p>
      </div>

      <div
        id="style_sl_s"
        class="absolute left-0 bg-gradient-to-b from-red-500/30 top-0 h-4 w-full"
      >
        <p class="flex justify-end items-end text-xs text-slate-400 mr-4 h-0">
          0.00
        </p>
      </div>
      <div
        id="style_tp_s"
        class="absolute left-0 bottom-0 bg-gradient-to-t from-green-500/30 h-4 w-full"
      ></div>

      <p id="time_s" class="text-4xl absolute right-20 text-slate-600">00:00</p>
    </div>

    <!-- look -->
    <div id="logDisplay">
      <!-- <div
        class="items-center bg-gradient-to-t from-[#00c45240] to-transparent p-3 rounded-lg border border-green-900"
      >
        <h1 class="text-2xl">
          <span class="bg-green-600 text-xl p-1 mr-2">LONG</span>BTC/USDT
        </h1>
        <p class="text-3xl text-green-400 my-2">
          1.45% <span class="text-gray-600 text-sm">SL</span>
        </p>
        <div class="flex justify-between">
          <div>
              <p class="text-white">10:14:46</p>
            <p class="text-gray-400 text-xs">2024-11-14</p>
            <p class="text-white">14654.12</p>
          </div>
          <div class="flex items-center">
            <p class="text-gray-400">-</p>
          </div>
          <div>
              <p class="text-white">10:14:46</p>
            <p class="text-gray-400 text-xs">2024-11-14</p>
            <p class="text-white">14654.12</p>
          </div>
        </div>
        <pre class="text-gray-500">SL : 4654.45</pre>
      </div>-->
    </div>
    <script>
      // Function to read the log.txt file and display its contents
      var current = null;
      var positions = [];
      var high_change = 0;
      var low_change = 0;
      let lastEmitTime = 0;

      loadLog();
      async function loadLog(logType) {
        positions.length = 0
        $(`#logDisplay`).empty();
        
        // look
        //const response = await fetch(`/log.txt`);
        const response = await fetch(`/log/` + logType);
        const text = await response.text();
        const linesArray = text.split(`
`);
        // console.log(linesArray);

        // L O G S

        if (logType) {
          $(`#logDisplay`).removeClass();
          linesArray.reverse().map((_, i) => {
            var cls = [``];
            if (_.includes(`=====`)) {
              if (_.includes(`LONG`)) {
                $(`#logDisplay`)
                  .append(`<div class="flex items-center mb-6 border-t border-b border-gray-800 bg-[#9333ea30]">
                    <div class="bg-green-600  px-1 mr-2 text-[10px]">LONG</div>
                    <pre class="text-purple-600" >${_}</pre>
                  </div>`);
              }
              if (_.includes(`SHORT`)) {
                $(`#logDisplay`)
                  .append(`<div class="flex items-center mb-6 border-t border-b border-gray-800 bg-[#9333ea30]">
                    <div class="bg-red-600 px-1 mr-2 text-[10px]">SHORT</div>
                    <pre class="text-purple-600" >${_}</pre>
                  </div>`);
              }
              return;
            }
            if (_.includes(`orderId`)) cls.push(`text-gray-400 text-xs`);
            if (_.includes(`EXIT`)) {
              if (_.includes(`EXIT SL`))
                cls.push(`text-pink-600 bg-[#db277730]`);
              if (_.includes(`MIN TARGET`))
                cls.push(`text-emerald-400 bg-[#34d39930]`);
              if (_.includes(`EXIT WIN`))
                cls.push(`text-green-400 bg-[#34d39930]`);
            }
            $(`#logDisplay`).append(`<pre class="${cls.join(` `)}">${_}</pre>`);
          });
          // CARDS
        } else {
          $(`#logDisplay`).addClass(`flex flex-wrap gap-2`);
          let temp_pos = {};
          linesArray.forEach((_, i) => {
            if (_.includes(`=====`)) {
              let l = _.split(" ");
              temp_pos.start_date = l[0];
              temp_pos.start_time = l[1];
              temp_pos.symbol = l[7];
              temp_pos.type = l[8];
              temp_pos.entry_price = l[11];
              temp_pos.sl = l[13];
            }

            if (_.includes(`EXIT`)) {
              let l = _.split(" ");
              temp_pos.end_date = l[0];
              temp_pos.end_time = l[1];
              temp_pos.status = l[7];
              temp_pos.change = l.at(-1);

              if (_.includes(`EXIT WIN`) || _.includes(`EXIT SL`)) {
                temp_pos.exit_price = l[8];
              }
              if (_.includes(`MIN TARGET`)) {
                temp_pos.exit_price = l[10];
              }

              temp_pos = {};
              positions.push(temp_pos);
            }
          });

          // C A R D S

          const data = positions.reverse();

          let loses = data.filter((_) => _.status == `SL`);
          let los = loses.length;
          let wins = data.length - los;
          $(`#los`).text(los);
          $(`#wins`).text(wins);

          $(`#los_bar`).css(`width`, (los / data.length) * 100 + `%`);
          $(`#wins_bar`).css(`width`, (wins / data.length) * 100 + `%`);

          data.map((pos, i) => {
            // check current position
            if (pos?.symbol && !pos?.exit_price) {
              current = pos;
              return;
            }

            if (!pos?.symbol) return;

            let isLoss = pos.status == `SL`;
            $(`#logDisplay`)
              .append(`<div class="items-center bg-gradient-to-t ${
              isLoss
                ? `from-[#c4004b20] border-red-900`
                : pos.change
                ? `from-[#00c45240] border-green-900`
                : `border-none`
            } to-transparent p-3 rounded-lg border ">
          <h1 class="text-2xl">
            <span class="${
              pos.type == `LONG` ? `bg-green-600` : `bg-red-600`
            } text-xs p-1 mr-2">${pos.type}</span>${pos.symbol}
          </h1>
          <p class="text-3xl ${
            isLoss ? `text-red-400` : `text-green-400`
          } my-2">
            ${pos.change ?? `_`} <span class="text-gray-600 text-sm">${
              pos.status
            }</span>
          </p>
          <div class="flex justify-between">
            <div>
                <p class="text-white">${pos.start_time.split(`,`)[0]}</p>
              <p class="text-gray-400 text-xs">${pos.start_date}</p>
              <p class="text-white">${pos.entry_price.replace(`,`, ``)}</p>
            </div>
            <div class="flex items-center">
              <p class="text-gray-400">-</p>
            </div>
            <div>
                <p class="text-white">${pos.end_time?.split(`,`)[0]}</p>
              <p class="text-gray-400 text-xs">${pos.end_date}</p>
              <p class="text-white">1${pos.exit_price}</p>
            </div>
          </div>
          <pre class="text-gray-500">SL : ${Number(pos.sl).toFixed(4)}</pre>
        </div>
      </div>`);
          });

          // A C T I V E   T R A D E

          function getPastHoursAndMinutes(timeString) {
            // Parse the input time string
            const [inputHours, inputMinutes, inputSeconds] = timeString
              .split(":")
              .map(Number);

            // Create a Date object for the current time
            const now = new Date();

            // Create a Date object for the input time
            const inputTime = new Date();
            inputTime.setHours(inputHours, inputMinutes, inputSeconds);

            // Calculate the difference in milliseconds
            const differenceMs = now - inputTime;

            // Convert the difference to hours and minutes
            const differenceMinutes = Math.floor(differenceMs / 1000 / 60); // Total minutes
            const hours = Math.floor(differenceMinutes / 60); // Extract hours
            const minutes = differenceMinutes % 60; // Extract remaining minutes

            // return { hours, minutes };
            if (hours == 0) return minutes + "m";
            return hours + "h " + minutes + "m";
          }

          // Helper function to calculate the percentage position of a price
          function calculatePosition(price, min, max) {
            return ((price - min) / (max - min)) * 100;
          }

          if (current) {
            // console.log({ current });

            const sl = Number(current.sl);
            const entry_price = Number(current.entry_price.replace(",", ""));
            let symbol = current.symbol.toLowerCase().replace("/", "");

            if (current.type == "LONG") {
              $("#active_short").addClass("hidden");
              $("#active_long").removeClass("hidden");

              $("#symbol").text(current.symbol);
              // Update the lines` positions
              $("#entry_line p").text(entry_price);
              $("#style_sl").find("p").text(sl);

              // // Establish a WebSocket connection to Binance`s trade stream for BTC/USDT
              const ws = new WebSocket(
                `wss://stream.binance.com:9443/ws/${symbol}@trade`
              );

              // // Event listener for when a new message is received from the WebSocket
              ws.onmessage = (event) => {
                // Parse the JSON data from the WebSocket message
                let trade = JSON.parse(event.data);

                // The `p` field contains the price of the trade (in USDT)
                let price = parseFloat(trade.p);
                const minPrice = sl;
                const maxPrice =
                  price < entry_price ? entry_price * 1.01 : price * 1.01; // 5%

                // Calculate positions
                const entryLinePosition = calculatePosition(
                  entry_price,
                  minPrice,
                  maxPrice
                );
                $("#entry_line").css("bottom", entryLinePosition + "%");
                $("#style_sl").css("height", entryLinePosition + "%");
                $("#style_tp").css("height", entryLinePosition + "%");

                // Log the current price to the console
                // console.log(`Current BTC/USDT Price: $${price}`);

                // Update the current price change percentage
                const changePercentage =
                  ((price - entry_price) / entry_price) * 100;

                $("#cur_change")
                  .text(changePercentage.toFixed(2) + "%")
                  .removeClass("text-green-400 text-red-400")
                  .addClass(
                    changePercentage > 0 ? "text-green-400" : "text-red-400"
                  );
                $("#cur_price").text(price);

                high_change =
                  changePercentage > high_change
                    ? changePercentage
                    : high_change;
                low_change =
                  changePercentage < low_change ? changePercentage : low_change;
                $("#high_change").text(high_change.toFixed(2) + "%");
                $("#low_change").text(low_change.toFixed(2) + "%");

                const curPriceLinePosition = calculatePosition(
                  price,
                  minPrice,
                  maxPrice
                );

                $("#cur_price_line")
                  .css("bottom", curPriceLinePosition + "%")
                  .css(
                    "background-color",
                    curPriceLinePosition > entryLinePosition
                      ? changePercentage > 1
                        ? "green"
                        : "blue"
                      : "orange"
                  );
                $("#cur_price_line").find("p").text(price);

                const now = Date.now();
                if (now - lastEmitTime >= 1000) {
                  // Check if 1 second has passed
                  lastEmitTime = now;
                  $("#time_s").text(
                    getPastHoursAndMinutes(current.start_time.split(`,`)[0])
                  );
                }
              };

              // Event listener for when the WebSocket connection is closed
              ws.onclose = () => {
                console.log("WebSocket connection closed");
              };

              // You can manually close the connection if needed by calling:
              // ws.close();
            }

            if (current.type == "SHORT") {
              $("#active_long").addClass("hidden");
              $("#active_short").removeClass("hidden");

              $("#symbol_s").text(current.symbol);
              // Update the lines` positions
              $("#entry_line_s").find("p").text(entry_price);
              $("#style_sl_s").find("p").text(sl);

              // // Establish a WebSocket connection to Binance`s trade stream for BTC/USDT
              const ws = new WebSocket(
                `wss://stream.binance.com:9443/ws/${symbol}@trade`
              );

              // // Event listener for when a new message is received from the WebSocket
              ws.onmessage = (event) => {
                // Parse the JSON data from the WebSocket message
                let trade = JSON.parse(event.data);

                // The `p` field contains the price of the trade (in USDT)
                let price = parseFloat(trade.p);

                const minPrice =
                  entry_price -
                  (price > entry_price ? entry_price * 0.01 : price * 0.01); // Maximum price (stop-loss area)
                const maxPrice = sl; // Maximum price (stop-loss area)

                // Update the current price change percentage
                const changePercentage =
                  ((price - entry_price) / entry_price) * 100;

                $("#cur_change_s")
                  .text(-changePercentage.toFixed(2) + "%")
                  .removeClass("text-green-400 text-red-400")
                  .addClass(
                    changePercentage < 0 ? "text-green-400" : "text-red-400"
                  );
                $("#cur_price_s").text(price);

                high_change =
                  -changePercentage > high_change
                    ? -changePercentage
                    : high_change;
                low_change =
                  -changePercentage < low_change
                    ? -changePercentage
                    : low_change;
                $("#high_change_s").text(high_change.toFixed(2) + "%");
                $("#low_change_s").text(low_change.toFixed(2) + "%");

                // Calculate line positions
                const entryLinePosition = calculatePosition(
                  entry_price,
                  minPrice,
                  maxPrice
                );
                // Update the entry line position
                $("#entry_line_s")
                  .css("bottom", entryLinePosition + "%")
                  .find("p")
                  .text(entry_price.toFixed(2));

                const curPriceLinePosition = calculatePosition(
                  price,
                  minPrice,
                  maxPrice
                );

                // Update the current price line position
                $("#cur_price_line_s")
                  .css("bottom", curPriceLinePosition + "%")
                  .css(
                    "background-color",
                    curPriceLinePosition < entryLinePosition
                      ? -changePercentage > 1
                        ? "green"
                        : "blue"
                      : "orange"
                  );
                // .find("p")
                // .text(price.toFixed(4));

                $("#cur_price_line_s").find("p").text(price);

                const slLinePosition = calculatePosition(
                  sl,
                  minPrice,
                  maxPrice
                );

                // Update the SL line position
                $("#style_sl_s")
                  .css("height", slLinePosition + "%")
                  .find("p")
                  .text(sl.toFixed(2));

                // Optional: Style the Take Profit (TP) zone
                $("#style_tp_s")
                  .css("height", entryLinePosition - curPriceLinePosition + "%")
                  .find("p")
                  .text("Take Profit"); // Add label dynamically

                const now = Date.now();
                if (now - lastEmitTime >= 1000) {
                  // Check if 1 second has passed
                  lastEmitTime = now;
                  $("#time_s").text(
                    getPastHoursAndMinutes(current.start_time.split(`,`)[0])
                  );
                }
              };

              // Event listener for when the WebSocket connection is closed
              ws.onclose = () => {
                console.log("WebSocket connection closed");
              };

              // You can manually close the connection if needed by calling:
              // ws.close();
            }
          }
        }

        // document.getElementById(`logDisplay`).textContent = text;
      }
    </script>
  </body>
</html>
'''
    return render_template_string(html_content)

@app.route('/log/<log_type>')
def get_log(log_type):
    # "Switch-like" logic using if-elif-else
    if log_type == 'scalp_log':
        return send_file(scalp_log, mimetype='text/plain')
    elif log_type == 'scalp_terminal':
        return send_file(scalp_terminal, mimetype='text/plain')
    if log_type == 'swing_log':
        return send_file(swing_log, mimetype='text/plain')
    elif log_type == 'swing_terminal':
        return send_file(swing_terminal, mimetype='text/plain')
    else:
        # Default case: send the default log file if log_type doesn't match
        return send_file(default_log_file, mimetype='text/plain')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
