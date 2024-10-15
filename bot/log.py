from flask import Flask, send_file, render_template_string

app = Flask(__name__)

# Paths to your log files
log_file_1 = '/home/ioss/Documents/Learn/bot-ui/bot/log.txt'
log_file_2 = '/home/ioss/Documents/Learn/bot-ui/bot/log_top_bot.txt'
default_log_file = log_file_1

@app.route('/')
def index():
    # HTML with two buttons to load different logs
    html_content = '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Log Viewer</title>
        <style>
            body {
                background-color: black;
                color: lime;
                font-family: 'Courier New', Courier, monospace;
                padding: 20px;
            }
            .log-container {
                white-space: pre-wrap;
                word-wrap: break-word;
                background-color: black;
                color: lime;
                border: 2px solid lime;
                padding: 20px;
                overflow-y: scroll;
                height: 70vh;
                width: 90vw;
            }
            button {
                background-color: lime;
                color: black;
                border: none;
                padding: 10px 20px;
                margin: 10px;
                font-size: 16px;
                cursor: pointer;
            }
            button:hover {
                background-color: #0a0;
            }
        </style>
    </head>
    <body>
        <h2>Log Viewer</h2>
        <button onclick="loadLog('log1')">Load Log 1</button>
        <button onclick="loadLog('log2')">Load Log 2</button>
        <div class="log-container" id="logDisplay"></div>

        <script>
            loadLog()
            async function loadLog(logType) {
                const response = await fetch('/log/' + logType);
                const text = await response.text();
                document.getElementById('logDisplay').textContent = text;
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
    app.run(debug=True)
