from flask import Flask, send_file, render_template_string

app = Flask(__name__)

# Paths to your log files
log_file_1 = '/home/ioss/Documents/Learn/future-bot/bot/log.txt'
log_file_2 = '/home/ioss/Documents/Learn/future-bot/bot/log.log'
default_log_file = log_file_1

@app.route('/')
def index():
    # HTML with two buttons to load different logs
    html_content = '''
<!DOCTYPE html>
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
    <button class="border border-green-400 p-2" onclick="loadLog(`log1`)">Scalp Log </button>
    <button class="border border-green-400 p-2"onclick="loadLog(`log2`)">Scalp Terminal</button>


    <div id="logDisplay"></div>

    <script>
      // Function to read the log.txt file and display its contents
      loadLog()

      async function loadLog(logType) {
        $(`#logDisplay`).empty()
        const response = await fetch(`/log/` + logType);
        const text = await response.text();
        const linesArray = text.split(`\n`).reverse();
        // console.log(linesArray);

        linesArray.map((_, i) => {
            var cls  = [``]

            if(_.includes(`=====`))cls.push(`text-green-400 mb-2`)
            if(_.includes(`orderId`))cls.push(`text-gray-400`)
            
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
    if log_type == 'log1':
        return send_file(log_file_1, mimetype='text/plain')
    elif log_type == 'log2':
        return send_file(log_file_2, mimetype='text/plain')
    else:
        # Default case: send the default log file if log_type doesn't match
        return send_file(default_log_file, mimetype='text/plain')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
