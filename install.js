module.exports = {
  run: [
    // Install torch first (with the correct CUDA build) so dependencies
    // don't pull in a CPU-only version. See torch.js for per-platform builds.
    {
      method: "script.start",
      params: {
        uri: "torch.js",
        params: {
          venv_python: "3.12",
          venv: "env",
          path: "."
        }
      }
    },
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
