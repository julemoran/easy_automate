const axios = require('axios');
function registerGetScreenshotNode(RED) {
    function GetScreenshotNode(config) {
        RED.nodes.createNode(this, config);
        this.on('input', async (msg) => {
            const sessionId = msg.session_id;
            if (!sessionId) {
                this.error("Missing session_id in msg for getScreenshot", msg);
                return;
            }
            const apiUrl = (msg.apiUrl || process.env.BROWSER_API_URL || `http://localhost:5000/browser/${sessionId}/screenshot`);
            try {
                const response = await axios.get(apiUrl, { responseType: 'arraybuffer' });
                msg.screenshot = Buffer.from(response.data, 'binary');
                this.send(msg);
            } catch (err) {
                this.error("Failed to get screenshot: " + (err.response?.data?.error || err.message), msg);
            }
        });
    }
    RED.nodes.registerType("browser-get-screenshot", GetScreenshotNode);
}

module.exports = registerGetScreenshotNode;
