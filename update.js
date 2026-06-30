module.exports = {
  run: [{
    method: "shell.run",
    params: {
      message: [
        "git checkout .",
        "git pull"
      ]
    }
  }]
}
