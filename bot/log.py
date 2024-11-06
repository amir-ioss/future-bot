from flask import Flask, send_file, render_template_string

app = Flask(__name__)

# Paths to your log files
scalp_log = '/home/ioss/Documents/Learn/future-bot/bot/scalp/log.txt'
scalp_terminal = '/home/ioss/Documents/Learn/future-bot/bot/log.log'

# scalp_log = '/home/ec2-user/bot/scalp/log.txt'
# scalp_terminal = '/home/ec2-user/bot/scalp/nohup.log'


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
    <h2 class="text-2xl">Log Viewer</h2>
    <button class="border border-green-400 p-2" onclick="loadLog(`scalp_log`)">Scalp Log </button>
    <button class="border border-green-400 p-2"onclick="loadLog(`scalp_terminal`)">Scalp Terminal</button>

    <button class="border border-green-400 p-2" onclick="loadLog(`swing_log`)">Swing Log </button>
    <button class="border border-green-400 p-2"onclick="loadLog(`swing_terminal`)">Swing Terminal</button>
    <div id="logDisplay"></div>
    <script>
      // Function to read the log.txt file and display its contents
      loadLog()
      async function loadLog(logType) {
        $(`#logDisplay`).empty()
        const response = await fetch(`/log/` + logType);
        const text = await response.text();
        const linesArray = text.split(`
`).reverse();
        // console.log(linesArray);
        linesArray.map((_, i) => {
            var cls  = [``]
            if(_.includes(`=====`)){
             if(_.includes(`LONG`)){
                $(`#logDisplay`).append(`<div class="flex items-center mb-6 border-t border-b border-gray-800 bg-[#9333ea30]">
                  <div class="bg-green-600  px-1 mr-2 text-[10px]">LONG</div>
                  <pre class="text-purple-600" >${_}</pre>
                </div>`)
              }
            if(_.includes(`SHORT`)){
                $(`#logDisplay`).append(`<div class="flex items-center mb-6 border-t border-b border-gray-800 bg-[#9333ea30]">
                  <div class="bg-red-600 px-1 mr-2 text-[10px]">SHORT</div>
                  <pre class="text-purple-600" >${_}</pre>
                </div>`)
              }
              return
            }
            if(_.includes(`orderId`))cls.push(`text-gray-400 text-xs`)
            if(_.includes(`EXIT`)){
              if(_.includes(`EXIT SL`))cls.push(`text-pink-600 bg-[#db277730]`)
              if(_.includes(`MIN TARGET`))cls.push(`text-emerald-400 bg-[#34d39930]`)
              if(_.includes(`EXIT WIN`))cls.push(`text-green-400 bg-[#34d39930]`)
            }
            $(`#logDisplay`).append(`<pre class="${cls.join(` `)}">${_}</pre>`)
        });
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
