module.exports = {
  daemon: true,
  run: [
    {
      method: "shell.run",
      params: {
        venv: "env",
        env: {
          PYTHONUNBUFFERED: "1"
        },
        path: "app",
        message: [
          "python ../video_app.py"
        ],
        on: [{
          // The regular expression pattern to monitor.
          // When this pattern occurs in the shell terminal, the shell will return,
          // and the script will go onto the next step.
          "event": "/(http:\\/\\/[0-9.:]+)/",

          // "done": true will move to the next step while keeping the shell alive.
          "done": true
        }]
      }
    },
    {
      // This step sets the local variable 'url'.
      // This local variable will be used in pinokio.js to display the "Open WebUI" tab when the value is set.
      method: "local.set",
      params: {
        // the input.event is the regular expression match object from the previous step
        // pattern has one capture group, so input.event[1] holds the exact url
        url: "{{input.event[1]}}"
      }
    }
  ]
}
