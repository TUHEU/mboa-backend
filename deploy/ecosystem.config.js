// PM2 config for the Contabo VPS.  Usage (from ~/mboa-backend):
//   pm2 start deploy/ecosystem.config.js && pm2 save
module.exports = {
  apps: [
    {
      name: "nyetam-api",
      script: ".venv/bin/uvicorn",
      interpreter: "none",
      args: "app.main:app --host 127.0.0.1 --port 8020",
      cwd: "/root/mboa-backend",
      max_memory_restart: "300M",
    },
  ],
};
