module.exports = {
  run: [
    // Create the Python environment and install the UI dependencies.
    // ffmpeg/ffprobe are provided by Pinokio's conda environment, so they
    // are NOT installed here.
    {
      method: "shell.run",
      params: {
        venv: "env",
        venv_python: "3.12",
        path: ".",
        message: [
          "python --version",
          "uv pip install -r requirements.txt"
        ]
      }
    }
  ]
}
