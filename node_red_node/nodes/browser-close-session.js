const axios = require('axios');
function registerCloseSessionNode(RED) {
    function CloseSessionNode(config) {
        RED.nodes.createNode(this, config);
        this.on('input', async (msg) => {
            const sessionId = msg.session_id;
            if (!sessionId) {
                this.error("Missing session_id in msg for closeSession", msg);
                return;
            }
            const apiUrl = (msg.apiUrl || process.env.BROWSER_API_URL || `http://localhost:5000/browser/${sessionId}/close`);
            try {
                await axios.post(apiUrl);
                msg.closed = true;
                this.send(msg);
            } catch (err) {
                this.error("Failed to close session: " + (err.response?.data?.error || err.message), msg);
            }
        });
    }
    RED.nodes.registerType("browser-close-session", CloseSessionNode);
}

module.exports = registerCloseSessionNode;
