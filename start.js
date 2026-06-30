module.exports = {
  daemon: true,
  run: [
    {
      method: "shell.run",
      params: {
        venv: "env",
        venv_python: "3.12",
        path: ".",
        env: {
          PYTHONUNBUFFERED: "1"
        },
        message: [
          "streamlit run app.py --server.port {{port}} --server.headless true --server.enableXsrfProtection false --server.enableCORS false --server.maxUploadSize 2048"
        ],
        on: [{
          event: "/(http:\\/\\/[0-9.:]+)/",
          done: true
        }]
      }
    },
    {
      method: "local.set",
      params: {
        url: "{{input.event[1]}}"
      }
    }
  ]
}
