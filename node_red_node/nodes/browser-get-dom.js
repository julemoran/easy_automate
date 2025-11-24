const axios = require('axios');
function registerGetDomNode(RED) {
    function GetDomNode(config) {
        RED.nodes.createNode(this, config);
        this.on('input', async (msg) => {
            const sessionId = msg.session_id;
            if (!sessionId) {
                this.error("Missing session_id in msg for getDom", msg);
                return;
            }
            const apiUrl = (msg.apiUrl || process.env.BROWSER_API_URL || `http://localhost:5000/browser/${sessionId}/dom`);
            try {
                const response = await axios.get(apiUrl);
                msg.dom = response.data || response;
                this.send(msg);
            } catch (err) {
                this.error("Failed to get DOM: " + (err.response?.data?.error || err.message), msg);
            }
        });
    }
    RED.nodes.registerType("browser-get-dom", GetDomNode);
}

module.exports = registerGetDomNode;
